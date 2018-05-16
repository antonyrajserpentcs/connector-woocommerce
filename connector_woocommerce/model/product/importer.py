# © 2009 Tech-Receptives Solutions Pvt. Ltd.
# © 2018 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# See LICENSE file for full copyright and licensing details.

import logging
import urllib.request
import urllib.error
import base64

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import MappingError

_logger = logging.getLogger(__name__)


class ProductBatchImporter(Component):

    """ Import the WooCommerce Partners.

    For every partner in the list, a delayed job is created.
    """
    _name = 'woo.product.product.batch.importer'
    _inherit = 'woo.delayed.batch.importer'
    _apply_on = ['woo.product.product']

    def _import_record(self, woo_id):
        """ Delay a job for the import """
        super(ProductBatchImporter, self)._import_record(
            woo_id)

    def run(self, filters=None):
        """ Run the synchronization """
        from_date = filters.pop('from_date', None)
        to_date = filters.pop('to_date', None)
        record_ids = self.backend_adapter.search(
            method='get',
            filters=filters,
            from_date=from_date,
            to_date=to_date,
        )
        _logger.info('search for woo Products %s returned %s',
                     filters, record_ids)
        for record_id in record_ids:
            self._import_record(record_id)


class ProductProductImporter(Component):
    _name = 'woo.product.product.importer'
    _inherit = 'woo.importer'
    _apply_on = ['woo.product.product']

    def _import_dependencies(self):
        """ Import the dependencies for the record"""
        record = self.woo_record
        record = record['product']
        for woo_category_id in record['categories']:
            self._import_dependency(woo_category_id,
                                    'woo.product.category')

    def _create(self, data):
        odoo_binding = super(ProductProductImporter, self)._create(data)
        # Adding Creation Checkpoint
        self.backend_record.add_checkpoint(odoo_binding)
        return odoo_binding

    def _update(self, binding, data):
        """ Update an Odoo record """
        super(ProductProductImporter, self)._update(binding, data)
        # Adding updation checkpoint
        #self.backend_record.add_checkpoint(binding)
        return

    def _before_import(self):
        """ Hook called before the import"""
        return

    def _after_import(self, binding):
        """ Hook called at the end of the import """
        image_importer = self.component(usage='product.image.importer')
        image_importer.run(self.external_id, binding.id)
        return


class ProductImageImporter(Component):

    """ Import images for a record.

    Usually called from importers, in ``_after_import``.
    For instance from the products importer.
    """
    _name = 'woo.product.image.importer'
    _inherit = 'woo.importer'
    _apply_on = ['woo.product.product']
    _usage = 'product.image.importer'

    def _get_images(self):
        return self.backend_adapter.get_images(self.woo_id)

    def _sort_images(self, images):
        """ Returns a list of images sorted by their priority.
        An image with the 'image' type is the the primary one.
        The other images are sorted by their position.

        The returned list is reversed, the items at the end
        of the list have the higher priority.
        """
        if not images:
            return {}
        # place the images where the type is 'image' first then
        # sort them by the reverse priority (last item of the list has
        # the the higher priority)

    def _get_binary_image(self, image_data):
        url = str(image_data.get('src')).replace("\\", '')
        try:
            request = urllib.request.Request(url)
            binary = urllib.request.urlopen(request)
        except urllib.error.HTTPError as err:
            if err.code == 404:
                # the image is just missing, we skip it
                return
            else:
                # we don't know why we couldn't download the image
                # so we propagate the error, the import will fail
                # and we have to check why it couldn't be accessed
                raise
        else:
            return binary.read()

    def run(self, woo_id, binding_id):
        self.woo_id = woo_id
        images = self._get_images()
        images = images['product']
        images = images['images']
        binary = None
        while not binary and images:
            binary = self._get_binary_image(images.pop())
        if not binary:
            return
        model = self.model.with_context(connector_no_export=True)
        binding = model.browse(binding_id)
        binding.write({'image': base64.b64encode(binary)})


class ProductProductImportMapper(Component):
    _name = 'woo.product.product.import.mapper'
    _inherit = 'woo.import.mapper'
    _apply_on = ['woo.product.product']

    direct = [
        ('description', 'description'),
        ('weight', 'weight'),
    ]

    @mapping
    def is_active(self, record):
        """Check if the product is active in Woo
        and set active flag in Odoo
        status == 1 in Woo means active"""
        if record['product']:
            rec = record['product']
            return {'active': rec['visible']}

    @mapping
    def in_stock(self, record):
        if record['product']:
            rec = record['product']
            return {'in_stock': rec['in_stock']}

    @mapping
    def name(self, record):
        if record['product']:
            rec = record['product']
            return {'name': rec['title']}

    @mapping
    def type(self, record):
        if record['product']:
            rec = record['product']
            if rec['type'] == 'simple':
                return {'type': 'product'}

    @mapping
    def categories(self, record):
        if record['product']:
            rec = record['product']
            woo_categories = rec['categories']
            binder = self.binder_for('woo.product.category')
            category_ids = []
            main_categ_id = None
            for woo_category_id in woo_categories:
                cat_id = binder.to_internal(woo_category_id, unwrap=True)
                if cat_id is None:
                    raise MappingError("The product category with "
                                       "woo id %s is not imported." %
                                       woo_category_id)
                category_ids.append(cat_id.id)
            if category_ids:
                main_categ_id = category_ids.pop(0)
            result = {'woo_categ_ids': [(6, 0, category_ids)]}
            if main_categ_id:  # Odoo assign 'All Products' if not specified
                result['categ_id'] = main_categ_id
            return result

    @mapping
    def price(self, record):
        """ The price is imported at the creation of
        the product, then it is only modified and exported
        from Odoo """
        if record['product']:
            rec = record['product']
            return {'list_price': rec and rec['price'] or 0.0}

    @mapping
    def sale_price(self, record):
        """ The price is imported at the creation of
        the product, then it is only modified and exported
        from Odoo """
        if record['product']:
            rec = record['product']
            return {'standard_price': rec and rec['sale_price'] or 0.0}

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    # Required for export
    @mapping
    def sync_data(self, record):
        if record.get('product'):
            return {'sync_data': True}

    @mapping
    def woo_backend_id(self, record):
        return {'woo_backend_id': self.backend_record.id}

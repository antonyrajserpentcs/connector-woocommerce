# -*- coding: utf-8 -*-
#
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech-Receptives(<http://www.techreceptives.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import logging
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import MappingError

_logger = logging.getLogger(__name__)


class CategoryBatchImporter(Component):

    """ Import the WooCommerce Product Categories.

    For every partner in the list, a delayed job is created.
    """

    _name = 'woo.product.category.batch.importer'
    _inherit = 'woo.delayed.batch.importer'
    _apply_on = 'woo.product.category'

    def _import_record(self, woo_id):
        """ Delay a job for the import """
        super(CategoryBatchImporter, self)._import_record(
            woo_id)

    def run(self, filters=None):
        """ Run the synchronization """
        from_date = filters.pop('from_date', None)
        to_date = filters.pop('to_date', None)
        #backend_adapter = self.component(usage='backend.adapter')
        record_ids = self.backend_adapter.search(
            filters,
            from_date=from_date,
            to_date=to_date,
        )
        _logger.info('search for woo Product Category %s returned %s',
                     filters, record_ids)
        for record_id in record_ids:
            self._import_record(record_id)


class ProductCategoryImporter(Component):
    _name = 'woo.product.category.importer'
    _inherit = 'woo.importer'
    _apply_on = ['woo.product.category']

    def _import_dependencies(self):
        """ Import the dependencies for the record"""
        record = self.woo_record
        # import parent category
        # the root category has a 0 parent_id
        record = record['product_category']
        if record['parent']:
            self._import_dependency(record.get('parent'), self.model)
        return

    def _create(self, data):
        odoo_binding = super(ProductCategoryImporter, self)._create(data)
        # Adding Creation Checkpoint
        self.backend_record.add_checkpoint(odoo_binding)
        return odoo_binding

    def _update(self, binding, data):
        """ Update an Odoo record """
        super(ProductCategoryImporter, self)._update(binding, data)
        # Adding updation checkpoint
        #self.backend_record.add_checkpoint(binding)
        return

    def _before_import(self):
        """ Hook called before the import"""
        return

    def _after_import(self, binding):
        """ Hook called at the end of the import """
        return


class ProductCategoryImportMapper(Component):
    _name = 'woo.product.category.import.mapper'
    _inherit = 'woo.import.mapper'
    _apply_on = 'woo.product.category'

    @mapping
    def name(self, record):
        if record['product_category']:
            rec = record['product_category']
            return {'name': rec['name']}

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    @mapping
    def parent_id(self, record):
        if record['product_category']:
            rec = record['product_category']
            if not rec['parent']:
                return
            binder = self.binder_for()
            # Get id of product.category model
            category_id = binder.to_internal(rec['parent'], unwrap=True)
            # Get id of woo.product.category model
            woo_cat_id = binder.to_internal(rec['parent'])
            if category_id is None:
                raise MappingError("The product category with "
                                   "woo id %s is not imported." %
                                   rec['parent'])
            return {'parent_id': category_id.id,
                    'woo_parent_id': woo_cat_id.id}

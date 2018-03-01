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
import xmlrpclib
from odoo import models, fields, api, _
from odoo.addons.connector.exception import IDMissingInBackend
from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class WooProductProduct(models.Model):
    _name = 'woo.product.product'
    _inherit = 'woo.binding'
    _inherits = {'product.product': 'odoo_id'}
    _description = 'woo product product'
    _rec_name = 'name'

    odoo_id = fields.Many2one(comodel_name='product.product',
                                 string='product',
                                 required=True,
                                 ondelete='cascade')
    backend_id = fields.Many2one(
        comodel_name='woo.backend',
        string='Woo Backend',
        store=True,
        readonly=False,
        required=True,
    )

    slug = fields.Char('Slung Name')
    credated_at = fields.Date('created_at')
    weight = fields.Float('weight')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    woo_categ_ids = fields.Many2many(
        comodel_name='product.category',
        string='Woo product category',
    )
    in_stock = fields.Boolean('In Stock')


class ProductProductAdapter(Component):
    _name = 'woo.product.product.adapter'
    _inherit = 'woo.adapter'
    _apply_on = 'woo.product.product'

    _woo_model = 'products/details'

    def _call(self, method, arguments):
        try:
            return super(ProductProductAdapter, self)._call(method, arguments)
        except xmlrpclib.Fault as err:
            # this is the error in the WooCommerce API
            # when the customer does not exist
            if err.faultCode == 102:
                raise IDMissingInBackend
            else:
                raise

    def search(self, filters=None, from_date=None, to_date=None):
        """ Search records according to some criteria and return a
        list of ids

        :rtype: list
        """
        if filters is None:
            filters = {}
        WOO_DATETIME_FORMAT = '%Y/%m/%d %H:%M:%S'
        dt_fmt = WOO_DATETIME_FORMAT
        if from_date is not None:
            # updated_at include the created records
            filters.setdefault('updated_at', {})
            filters['updated_at']['from'] = from_date.strftime(dt_fmt)
        if to_date is not None:
            filters.setdefault('updated_at', {})
            filters['updated_at']['to'] = to_date.strftime(dt_fmt)

        return self._call('products/list',
                          [filters] if filters else [{}])

    def get_images(self, id, storeview_id=None):
        return self._call('products/' + str(id), [int(id), storeview_id, 'id'])

    def read_image(self, id, image_name, storeview_id=None):
        return self._call('products',
                          [int(id), image_name, storeview_id, 'id'])

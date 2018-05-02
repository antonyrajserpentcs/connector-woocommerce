# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import logging
import xmlrpc.client as xmlrpclib
from odoo import api, fields, models
from odoo.addons.connector.exception import IDMissingInBackend
from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class WooProductCategory(models.Model):
    _name = 'woo.product.category'
    _inherit = 'woo.binding'
    _inherits = {'product.category': 'odoo_id'}
    _description = 'Woo Product Category'

    _rec_name = 'name'

    odoo_id = fields.Many2one(comodel_name='product.category',
                                 string='category',
                                 required=True,
                                 ondelete='cascade')
    backend_id = fields.Many2one(
        comodel_name='woo.backend',
        string='Woo Backend',
        store=True,
        readonly=False,
    )

    slug = fields.Char('Slung Name')
    woo_parent_id = fields.Many2one(
        comodel_name='woo.product.category',
        string='Woo Parent Category',
        ondelete='cascade',)
    description = fields.Char('Description')
    count = fields.Integer('count')
    woo_child_ids = fields.One2many(
        comodel_name='woo.product.category',
        inverse_name='woo_parent_id',
        string='Woo Child Categories',
    )


class ProductCategory(models.Model):
    _inherit = 'product.category'

    woo_bind_ids = fields.One2many(
        comodel_name='woo.product.category',
        inverse_name='odoo_id',
        string="Woo Bindings",
    )


class CategoryAdapter(Component):
    _name = 'woo.product.category.adapter'
    _inherit = 'woo.adapter'
    _apply_on = 'woo.product.category'

    _woo_model = 'products/categories'

    def _call(self, method, arguments):
        try:
            return super(CategoryAdapter, self)._call(method, arguments)
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
            filters.setdefault('updated_at', {})
            filters['updated_at']['from'] = from_date.strftime(dt_fmt)
        if to_date is not None:
            filters.setdefault('updated_at', {})
            filters['updated_at']['to'] = to_date.strftime(dt_fmt)
        return self._call('products/categories/list',
                          [filters] if filters else [{}])

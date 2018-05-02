# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import logging
import xmlrpc.client as xmlrpclib
from odoo import models, fields, api
from odoo.addons.component.core import Component
from odoo.addons.connector.exception import IDMissingInBackend

_logger = logging.getLogger(__name__)


class WooResPartner(models.Model):
    _name = 'woo.res.partner'
    _inherit = 'woo.binding'
    _inherits = {'res.partner': 'odoo_id'}
    _description = 'woo res partner'

    _rec_name = 'name'

    odoo_id = fields.Many2one(comodel_name='res.partner',
                                 string='Partner',
                                 required=True,
                                 ondelete='cascade')
    backend_id = fields.Many2one(
        comodel_name='woo.backend',
        string='Woo Backend',
        store=True,
        readonly=False,
    )


class ResPartner(models.Model):
    _inherit = 'res.partner'

    woo_bind_ids = fields.One2many(
        comodel_name='woo.res.partner',
        inverse_name='odoo_id',
        string="Woo Bindings",
    )


class CustomerAdapter(Component):
    _name = 'woo.partner.adapter'
    _inherit = 'woo.adapter'
    _apply_on = 'woo.res.partner'

    _woo_model = 'customers'

    def _call(self, method, arguments):
        try:
            return super(CustomerAdapter, self)._call(method, arguments)
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
        # the search method is on ol_customer instead of customer
        return self._call('customers/list',
                          [filters] if filters else [{}])

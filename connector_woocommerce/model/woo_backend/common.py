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
from contextlib import contextmanager

from odoo import models, api, fields, _
from woocommerce import API
from odoo.exceptions import Warning
from datetime import datetime
from ...components.backend_adapter import WooLocation, WooAPI


class WcBackend(models.Model):
    _name = 'woo.backend'
    _inherit = 'connector.backend'
    _description = 'WooCommerce Backend Configuration'

    name = fields.Char(string='name')
    location = fields.Char("Url")
    consumer_key = fields.Char("Consumer key")
    consumer_secret = fields.Char("Consumer Secret")
    version = fields.Selection([('v2', 'V2')], 'Version')
    verify_ssl = fields.Boolean("Verify SSL")
    default_lang_id = fields.Many2one(
        comodel_name='res.lang',
        string='Default Language',
        help="If a default language is selected, the records "
             "will be imported in the translation of this language.\n"
             "Note that a similar configuration exists "
             "for each storeview.",
    )

    @contextmanager
    @api.multi
    def work_on(self, model_name, **kwargs):
        self.ensure_one()
        lang = self.default_lang_id
        if lang.code != self.env.context.get('lang'):
            self = self.with_context(lang=lang.code)
        woo_location = WooLocation(
            self.location,
            self.consumer_key,
            self.consumer_secret,
        )
        with WooAPI(woo_location) as woo_api:
            _super = super(WcBackend, self)
            # from the components we'll be able to do: self.work.woo_api
            with _super.work_on(
                    model_name, woo_api=woo_api, **kwargs) as work:
                yield work

    @api.multi
    def get_product_ids(self, data):
        product_ids = [x['id'] for x in data['products']]
        product_ids = sorted(product_ids)
        return product_ids

    @api.multi
    def get_product_category_ids(self, data):
        product_category_ids = [x['id'] for x in data['product_categories']]
        product_category_ids = sorted(product_category_ids)
        return product_category_ids

    @api.multi
    def get_customer_ids(self, data):
        customer_ids = [x['id'] for x in data['customers']]
        customer_ids = sorted(customer_ids)
        return customer_ids

    @api.multi
    def get_order_ids(self, data):
        order_ids = self.check_existing_order(data)
        return order_ids

    @api.multi
    def update_existing_order(self, woo_sale_order, data):
        """ Enter Your logic for Existing Sale Order """
        return True

    @api.multi
    def check_existing_order(self, data):
        order_ids = []
        for val in data['orders']:
            woo_sale_order = self.env['woo.sale.order'].search(
                [('external_id', '=', val['id'])])
            if woo_sale_order:
                self.update_existing_order(woo_sale_order[0], val)
                continue
            order_ids.append(val['id'])
        return order_ids

    @api.multi
    def test_connection(self):
        location = self.location
        cons_key = self.consumer_key
        sec_key = self.consumer_secret
        version = 'v3'
        wcapi = API(url=location,
                    consumer_key=cons_key,
                    consumer_secret=sec_key,
                    version=version,
                    query_string_auth=True
                    )
        r = wcapi.get("products")
        if r.status_code == 404:
            raise Warning(_("Enter Valid url"))
        val = r.json()
        msg = ''
        if 'errors' in r.json():
            msg = val['errors'][0]['message'] + '\n' + \
            val['errors'][0]['code']
            raise Warning(_(msg))
        else:
            raise Warning(_('Test Success'))
        return True

    @api.multi
    def import_category(self):
        import_start_time = datetime.now()
        backend = self
        from_date = None
        self.env['woo.product.category'].with_delay().import_batch(
                backend,
                filters={'from_date': from_date,
                         'to_date': import_start_time},
            )
        return True

    @api.multi
    def import_product(self):
        import_start_time = datetime.now()
        backend = self
        from_date = None
        self.env['woo.product.product'].with_delay().import_batch(
                backend,
                filters={'from_date': from_date,
                         'to_date': import_start_time},
            )
        return True

    @api.multi
    def import_customer(self):
        import_start_time = datetime.now()
        backend = self
        from_date = None
        self.env['woo.res.partner'].with_delay().import_batch(
                backend,
                filters={'from_date': from_date,
                         'to_date': import_start_time}
            )
        return True

    @api.multi
    def import_order(self):
        import_start_time = datetime.now()
        backend = self
        from_date = None
        self.env['woo.sale.order'].with_delay().import_batch(
                backend,
                filters={'from_date': from_date,
                         'to_date': import_start_time}
            )
        return True

    @api.multi
    def import_categories(self):
        """ Import Product categories from WooCommerce site """
        for backend in self:
            backend.import_category()
        return True

    @api.multi
    def import_products(self):
        """ Import Products from WooCommerce  site """
        for backend in self:
            backend.import_product()
        return True

    @api.multi
    def import_customers(self):
        """ Import Customers from WooCommerce  site """
        for backend in self:
            backend.import_customer()
        return True

    @api.multi
    def import_orders(self):
        """ Import Orders from WooCommerce  site """
        for backend in self:
            backend.import_order()
        return True

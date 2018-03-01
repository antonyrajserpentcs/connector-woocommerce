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

from odoo.addons.component.core import Component


class WooModelBinder(Component):
    """ Bind records and give odoo/woo ids correspondence

    Binding models are models called ``woo.{normal_model}``,
    like ``woo.res.partner`` or ``woo.product.product``.
    They are ``_inherits`` of the normal models and contains
    the Woo ID, the ID of the Woo Backend and the additional
    fields belonging to the Woo instance.
    """
    _name = 'woo.binder'
    _inherit = ['base.binder', 'base.woo.connector']
    _apply_on = [
        'woo.res.partner',
        'woo.product.category',
        'woo.product.product',
        'woo.sale.order',
        'woo.sale.order.line',
    ]

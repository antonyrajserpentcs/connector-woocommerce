# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo.addons.component.core import AbstractComponent


class BaseWooConnectorComponent(AbstractComponent):
    """ Base Woo Connector Component

    All components of this connector should inherit from it.
    """

    _name = 'base.woo.connector'
    _inherit = 'base.connector'
    _collection = 'woo.backend'

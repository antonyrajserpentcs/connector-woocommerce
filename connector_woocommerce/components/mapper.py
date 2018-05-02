# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo.addons.component.core import AbstractComponent


class WooImportMapper(AbstractComponent):
    _name = 'woo.import.mapper'
    _inherit = ['base.woo.connector', 'base.import.mapper']
    _usage = 'import.mapper'


def normalize_datetime(field):
    """Change a invalid date which comes from Woo, if
    no real date is set to null for correct import to
    Odoo"""

    def modifier(self, record, to_attr):
        if record[field] == '0000-00-00 00:00:00':
            return None
        return record[field]
    return modifier

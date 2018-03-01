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

from odoo import api, models, fields
from odoo.addons.queue_job.job import job, related_action


class WooBinding(models.AbstractModel):
    """ Abstract Model for the Bindings.

    All the models used as bindings between Woo and Odoo
    (``woo.res.partner``, ``woo.product.product``, ...) should
    ``_inherit`` it.
    """
    _name = 'woo.binding'
    _inherit = 'external.binding'
    _description = 'Woo Binding (abstract)'

    # odoo_id = odoo-side id must be declared in concrete model
    backend_id = fields.Many2one(
        comodel_name='woo.backend',
        string='Woo Backend',
        required=True,
        ondelete='restrict',
    )
    # fields.Char because 0 is a valid Woo ID
    external_id = fields.Char(string='ID on Woo')

    _sql_constraints = [
        ('woo_uniq', 'unique(backend_id, external_id)',
         'A binding already exists with the same Woo ID.'),
    ]

    @job(default_channel='root.woo')
    @api.model
    def import_batch(self, backend, filters=None):
        """ Prepare the import of records modified on Woo """
        if filters is None:
            filters = {}
        with backend.work_on(self._name) as work:
            importer = work.component(usage='batch.importer')
            return importer.run(filters=filters)

    @job(default_channel='root.woo')
    @related_action(action='related_action_woo_link')
    @api.model
    def import_record(self, backend, external_id, force=False):
        """ Import a Woo record """
        with backend.work_on(self._name) as work:
            importer = work.component(usage='record.importer')
            return importer.run(external_id, force=force)

# © 2009 Tech-Receptives Solutions Pvt. Ltd.
# © 2018 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import Warning


class WooExport(models.TransientModel):
    """
    Fields which are declared here must be passed also in
    "context" on woo export wizard action as woo_active_field.
    "context" values are case sensitive.
    <field name="context">{'woo_active_field': 'partner_ids'}</field>
    """
    _name = 'wizard.woo.export'
    _description = 'Wizard to export to WooCommerce.'

    @api.model
    def default_get(self, fields):
        res = super(WooExport, self).default_get(fields)
        context = self.env.context
        # target_field and active_ids are passed through context from action.
        active_field = context.get('woo_active_field')
        active_ids = context.get('active_ids')
        # Load the values
        res[active_field] = active_ids
        return res

    product_cate_ids = fields.Many2many(
        'product.category',
        string='Product Categories'
    )
    product_ids = fields.Many2many(
        'product.product',
        string='Products'
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Partners'
    )
    order_ids = fields.Many2many(
        'sale.order',
        string='Sale Orders'
    )

    @api.multi
    def woo_export(self):
        """"
        This method exports the Odoo data to WooCommerce.
        Object and methods are managed dynamically based on context values.
        Woo Backend Id is mandatory for exporting.
        @param: self (Current Object)
        @return: True
        @type: Boolean
        """
        context = self.env.context
        active_field = context.get('woo_active_field')
        active_model = context.get('active_model')
        for rec in self:
            # browse data of active_model with active_ids
            active_field_ids = getattr(rec, str(active_field))
            import_obj = rec.env["woo.%s" % active_model]
            for active_id in active_field_ids:
                if not active_id.woo_backend_id:
                    raise Warning(_(
                        "WooCommerce Backend is missing! \n"
                        " Record : %s\n"
                        " ID : %s" %
                        (active_id.display_name, active_id.id)
                    ))
                is_woo_data = import_obj.search([
                                ('odoo_id', '=', active_id.id)], limit=1)
                if is_woo_data:
                    #Do the export
                    is_woo_data.with_delay().export_record()
                else:
                    # Build environment to export
                    import_id = import_obj.create({
                        'backend_id': active_id.woo_backend_id.id,
                        'odoo_id': active_id.id,
                    })
                    import_id.with_delay().export_record()
            return True

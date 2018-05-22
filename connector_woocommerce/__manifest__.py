# © 2009 Tech-Receptives Solutions Pvt. Ltd.
# © 2018 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# See LICENSE file for full copyright and licensing details.

{
    'name': 'WooCommerce Connector',
    'version': '11.0.1.0.1',
    'category': 'customized',
    'description': """WooCommerce Connector.""",
    'author': """Tech Receptives,
                Serpent Consulting Services Pvt. Ltd.,
                Odoo Community Association (OCA).""",
    'contributors': """Tech Receptives,
                       Serpent Consulting Services Pvt. Ltd.""",
    'maintainer': 'Odoo Community Association (OCA)',
    'website': 'http://www.openerp.com',
    'summary': """Imports the Product's Categories, Products, Customers and
                Sale orders from WooCommerce, Meanwhile Exports from Odoo
                To WooCommerce.""",
    'depends': ['base', 'connector', 'connector_ecommerce'],
    'installable': True,
    'auto_install': False,
    'data': [
        "security/ir.model.access.csv",
        "views/backend_view.xml",
        "views/product_view.xml",
        "views/res_partner_views.xml",
        "views/sale_views.xml",
        "wizard/woo_export_view.xml",
    ],
    'external_dependencies': {
        'python': ['woocommerce'],
    },
    'application': True,
    "sequence": 3,
}

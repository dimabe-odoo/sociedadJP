from odoo import fields, models, api


class PurchaseOrder (models.Model):
    _inherit = 'purchase.order'

    have_purchase_without_supply = fields.Boolean('¿Tiene compra comodato?')



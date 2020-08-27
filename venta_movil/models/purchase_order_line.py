from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    purchase_without_supply = fields.Integer('Compra comodato')
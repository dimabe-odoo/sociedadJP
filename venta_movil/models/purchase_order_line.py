from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    purchase_without_supply = fields.Integer('Compra comodato')

    @api.onchange('purchase_without_supply')
    def onchange_purchase_without_supply(self):
        if self.product_qty < self.purchase_without_supply:
            raise models.ValidationError(
                'La cantidad de de compra comodato no puede ser mayor a la cantidad solicitidad')

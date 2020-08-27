from odoo import fields, models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    purchase_without_supply = fields.Float('Comprar comodato')

    @api.onchange
    def on_change_qty(self):
        if self.product_uom_qt < self.purchase_without_supply:
            raise models.ValidationError('Error')
    



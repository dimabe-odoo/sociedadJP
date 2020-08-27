from odoo import fields, models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    purchase_without_supply = fields.Integer('Comprar comodato')

    @api.onchange
    def on_change_qty(self):
        if self.product_qty < self.
    



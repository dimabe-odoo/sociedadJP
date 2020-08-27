from odoo import fields, models, api
from odoo.addons import decimal_precision as dp


class StockMove(models.Model):
    _inherit = 'stock.move'

    purchase_without_supply = fields.Float('Comprar comodato', digits=dp.get_precision('Product Unit of Measure'))

    @api.onchange
    def on_change_qty(self):
        if self.product_uom_qt < self.purchase_without_supply:
            raise models.ValidationError('Error')

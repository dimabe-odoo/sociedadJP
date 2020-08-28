from odoo import fields, models, api
from odoo.addons import decimal_precision as dp


class StockMove(models.Model):
    _inherit = 'stock.move'

    purchase_without_supply = fields.Float('Comprar comodato', digits=dp.get_precision('Product Unit of Measure'))

    loan_supply = fields.Float('Prestamo',digits=dp.get_precision('Product Unit of Measure'))

    @api.onchange('purchase_without_supply')
    def on_change_qty(self):
        if self.product_uom_qty < self.purchase_without_supply:
            raise models.ValidationError('La compra comodato no puede ser mayor a la demanda')

    @api.onchange('loan_supply')
    def on_change_qty(self):
        if self.product_uom_qty < self.loan_supply:
            raise models.ValidationError('El prestamo no puede ser mayor a la demanda')

from odoo import models, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'


def button_validate(self):
    for stock_picking in self:
        raise models.ValidationError(stock_picking)
        message = ''
        product = self.env['product.product'].browse(stock_picking.product_ids[0].id)
        available_qty = product.with_context({'warehouse' : stock_picking.warehouse_id}).qty_available
        if stock_picking.quantity_done < 


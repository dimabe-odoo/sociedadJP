from odoo import models, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'


    def button_validate(self):
        for stock_picking in self:
            message = ''
            supply = self.env['product.product'].browse(stock_picking.move_ids_without_package[0].supply_id)
            available_qty = supply.with_context({'warehouse' : stock_picking.warehouse_id}).qty_available
            raise models.ValidationError(available_qty)
            #if stock_picking.quantity_done < 


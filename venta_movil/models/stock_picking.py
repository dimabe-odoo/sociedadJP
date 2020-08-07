from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        for stock_picking in self:
            message = ''
            for move in stock_picking.move_ids_without_package:
                if move.product_id.supply_id:
                    supply_id = move.product_id.supply_id.id
                    quant = self.env['stock.quant'].search(
                        [('product_id', '=', supply_id), ('location_id', '=', stock_picking.location_dest_id.id)])
                    raise models.ValidationError(quant.quantity)
                # if stock_picking.quantity_done <
                res = super(MrpWorkorder, self).button_validate()
                return res

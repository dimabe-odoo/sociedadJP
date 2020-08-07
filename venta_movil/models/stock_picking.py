from odoo import models, fields
import datetime


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        for stock_picking in self:
            message = ''
            stock_moves = []

            for move in stock_picking.move_ids_without_package:
                if move.product_id.supply_id:
                    supply_id = move.product_id.supply_id
                    quant = self.env['stock.quant'].search(
                        [('product_id', '=', supply_id.id), ('location_id', '=', stock_picking.location_dest_id.id)])
                    if quant.quantity < move.product_uom_qty:
                        raise models.UserError('No tiene la cantidad necesaria de insumos {}'.format(
                            supply_id.display_name))
                    stock_moves.append({
                        'company_id': self.env.user.company_id.id,
                        'date': datetime.datetime.now(),
                        'location_id': stock_picking.location_dest_id.id,
                        'product_id': supply_id.id,
                        'product_uom': supply_id.uom_id.id,
                        'product_uom_qty': move.product_uom_qty
                    })
                # if stock_picking.quantity_done <

            res = super(StockPicking, self).button_validate()
            if res:
                if stock_picking.picking_type_code == 'outgoing':
                    name = 'IN/{}'.format(stock_picking.name)
                    dispatch = self.env['stock.picking'].create({
                        'name': name,
                        'picking_type_code': 'incoming',
                        'origin': stock_picking.origin,
                        'state': 'done',
                        'date_done': datetime.datetime.now(),
                        'picking_type_id': self.env['stock.picking.type'].search(
                            [('default_location_src_id', '=', stock_picking.location_dest_id.id),
                             ('sequence_code', '=', 'IN')]).id,
                        'partner_id': stock_picking.partner_id.id
                    })
                    location_dest = self.env['stock.location'].search([('name', '=', 'Customers')])
                else:
                    name = 'OUT/{}'.format(stock_picking.name)
                    dispatch = self.env['stock.picking'].create({
                        'name': name,
                        'picking_type_code': 'outgoing',
                        'origin': stock_picking.origin,
                        'date_done': datetime.datetime.now(),
                        'location_id': stock_picking.location_dest_id.id,
                        'picking_type_id': self.env['stock.picking.type'].search(
                            [('default_location_src_id', '=', stock_picking.location_dest_id.id),
                             ('sequence_code', '=', 'OUT')]).id,
                        'state': 'done',
                        'partner_id': stock_picking.partner_id.id
                    })
                    location_dest = self.env['stock.location'].search([('name', '=', 'Vendors')])
                for stock in stock_moves:
                    move = self.env['stock.move'].create({
                        'name': dispatch.name,
                        'picking_id': dispatch.id,
                        'company_id': stock['company_id'],
                        'date': stock['date'],
                        'location_id': stock['location_id'],
                        'location_dest_id': location_dest.id,
                        'state': 'done',
                        'product_id': stock['product_id'],
                        'product_uom': stock['product_uom'],
                        'product_uom_qty': stock['product_uom_qty']
                    })
                    raise models.ValidationError(move)
                    self.env['stock.move.line'].create({
                        'move_id': move.id,
                        'company_id': stock['company_id'],
                        'date': stock['date'],
                        'state': 'done',
                        'location_id': stock['location_id'],
                        'product_id': stock['product_id'],
                        'product_uom_id': stock['product_uom'],
                        'qty_done': move.product_uom_qty,
                        'location_dest_id': move.location_dest_id.id,
                    })
            return res

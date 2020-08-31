from odoo import fields, models, api
import datetime


class PosOrder(models.Model):
    _inherit = 'pos.order'

    supply_reception_id = fields.Many2one('stock.picking', 'Recepcion de Insumos')

    def create_picking(self):
        res = super(PosOrder, self).create_picking()
        picking = self.env['stock.picking'].create({
            'name': 'POS/IN/' + item.name,
            'picking_type_code': 'incoming',
            'picking_type_id': self.env['stock.picking.type'].search(
                [('warehouse_id.id', '=', item.picking_type_id.warehouse_id.id),
                 ('sequence_code', '=', 'IN')]).id,
            'location_id': self.env['stock.location'].search([('name', '=', 'Customers')]).id,
            'location_dest_id': self.env['stock.warehouse'].search(
                [('id', '=', item.picking_type_id.warehouse_id.id)]).lot_stock_id.id,
            'state': 'assigned',
            'date_done': datetime.datetime.now(),
            'origin': 'Entrada de ' + item.origin,
            'partner_id': item.partner_id.id
        })
        for line in self.lines:
            if line.product_id.supply_id:
                stock_move = self.env['stock.move'].create({
                    'name': picking.name,
                    'picking_id': picking.id,
                    'product_id': line.product_id.supply_id.id,
                    'product_uom': line.product_id.uom_id.id,
                    'product_uom_qty': line.qty,
                    'state': 'confirmed',
                    'location_id': reception.location_id.id,
                    'location_dest_id': picking.location_dest_id.id,
                    'date': datetime.datetime.now(),
                    'company_id': self.env.user.company_id.id
                })
                self.env['stock.move.line'].create({
                    'picking_id': stock_move.picking_id.id,
                    'move_id': stock_move.id,
                    'product_id': stock_move.product_id.id,
                    'product_uom_id': stock_move.product_uom.id,
                    'qty_done': stock_move.product_uom_qty,
                    'state': 'confirmed',
                    'company_id': stock_move.company_id.id,
                    'location_id': stock_move.location_id.id,
                    'location_dest_id': stock_move.location_dest_id.id
                })
                picking.button_validate()
                models._logger.error('Picking {}'.format(picking.values()))
                self.picking_id.write({
                    'supply_dispatch_id': picking.id,
                    'show_supply': True
                })
                self.write({
                    'supply_reception_id': picking.id
                })
        return res

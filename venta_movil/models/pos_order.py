from odoo import fields, models, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def create_picking(self):
        super(PosOrder, self).create_picking()
        for line in lines:
            if line.product_id.supply_id:
                reception = self.env['stock.picking'].create({
                    'name': 'POS/IN/' + self.picking_id.name,
                    'picking_type_code': 'incoming',
                    'picking_type_id': self.env['stock.picking.type'].search(
                        [('warehouse_id.id', '=', self.picking_type_id.warehouse_id.id),
                         ('sequence_code', '=', 'IN')]).id,
                    'location_id': self.env['stock.location'].search([('name', '=', 'Customers')]).id,
                    'location_dest_id': self.env['stock.warehouse'].search(
                        [('id', '=', self.picking_type_id.warehouse_id.id)]).lot_stock_id.id,
                    'state': 'assigned',
                    'date_done': datetime.datetime.now(),
                    'origin': self.picking_id.origin,
                    'partner_id': self.partner_id.id
                })
                stock_move = self.env['stock.move'].create({
                    'name': reception.name,
                    'picking_id': reception.id,
                    'product_id': line.product_id.supply_id.id,
                    'product_uom': line.product_id.uom_id.id,
                    'product_uom_qty': line.product_uom_qty,
                    'state': 'confirmed',
                    'location_id': line.location_id.id,
                    'location_dest_id': line.location_dest_id.id,
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
                reception.button_validate()
                self.picking_id.write({
                    'supply_dispatch_id': reception.id,
                    'show_supply': True
                })

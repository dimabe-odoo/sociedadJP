from odoo import fields, models, api
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    loan_supply = fields.Boolean('¿Es prestamo de cilindro?')

    supply_reception_id = fields.Many2one('stock.picking', 'Entrada de insumo')

    def action_confirm(self):
        self.ensure_one()
        if not self.loan_supply:
            for line in self.order_line:
                if line.product_id.supply_id:
                    stock_picking = self.env['stock.picking'].create({
                        'partner_id': self.partner_id.id,
                        'location_id': self.env['stock.location'].search([('name', '=', 'Customers')]).id,
                        'location_dest_id': self.warehouse_id.lot_stock_id.id,
                        'picking_type_id': self.env['stock.picking.type'].search(
                            [('sequence_code', '=', 'IN'), ('warehouse_id', '=', self.warehouse_id.id)]).id,
                        'origin': self.name,
                        'company_id': self.env.user.company_id.id
                    })
                    stock_picking.write({
                        'name': 'SUPPLY/'+stock_picking.name
                    })
                    stock_move = self.env['stock.move'].create({
                        'name': 'SUPPLY/' + stock_picking.name,
                        'picking_id': stock_picking.id,
                        'reference': 'SUPPLY/' + stock_picking.name,
                        'company_id': self.env.user.company_id.id,
                        'date': datetime.now(),
                        'location_id': self.env['stock.location'].search([('name', '=', 'Customers')]).id,
                        'location_dest_id': self.warehouse_id.lot_stock_id.id,
                        'state': 'confirmed',
                        'product_id': line.product_id.supply_id.id,
                        'product_uom': line.product_uom.id,
                        'product_uom_qty': line.product_uom_qty
                    })
                    self.env['stock.move.line'].create({
                        'move_id': stock_move.id,
                        'reference': 'SUPPLY/' + stock_picking.name,
                        'picking_id': stock_picking.id,
                        'company_id': self.env.user.company_id.id,
                        'date': datetime.now(),
                        'location_id': self.env['stock.location'].search([('name', '=', 'Customers')]).id,
                        'location_dest_id': self.warehouse_id.lot_stock_id.id,
                        'product_id': line.product_id.supply_id.id,
                        'product_uom_id': line.product_uom.id,
                        'qty_done': line.product_uom_qty
                    })
                    self.write({
                        'supply_reception_id': stock_picking.id
                    })
            super(SaleOrder, self).action_confirm()
        else:
            for line in self.order_line:
                if line.product_id.supply_id:
                    stock_picking = self.env['stock.picking'].create({
                        'partner_id': self.partner_id.id,
                        'location_id': self.env['stock.location'].search([('name', '=', 'Customers')]).id,
                        'location_dest_id': self.warehouse_id.loan_location_id.id,
                        'picking_type_id': self.env['stock.picking.type'].search(
                            [('sequence_code', '=', 'IN'), ('warehouse_id', '=', self.warehouse_id.id)]).id,
                        'origin': self.name,
                        'company_id': self.env.user.company_id.id
                    })
                    stock_picking.write({
                        'name': 'LOAN/'+stock_picking.name
                    })
                    stock_move = self.env['stock.move'].create({
                        'name': 'SUPPLY/' + stock_picking.name,
                        'picking_id': stock_picking.id,
                        'company_id': self.env.user.company_id.id,
                        'date': datetime.now(),
                        'location_id': self.env['stock.location'].search([('name', '=', 'Customers')]).id,
                        'location_dest_id': self.warehouse_id.lot_stock_id.id,
                        'state': 'confirmed',
                        'product_id': line.product_id.supply_id.id,
                        'product_uom': line.product_uom.id,
                        'product_uom_qty': line.product_uom_qty
                    })
                    self.env['stock.move.line'].create({
                        'move_id': stock_move.id,
                        'picking_id': stock_picking.id,
                        'company_id': self.env.user.company_id.id,
                        'date': datetime.now(),
                        'location_id': self.env['stock.location'].search([('name', '=', 'Customers')]).id,
                        'location_dest_id': self.warehouse_id.lot_stock_id.id,
                        'product_id': line.product_id.supply_id.id,
                        'product_uom_id': line.product_uom.id,
                        'qty_done': line.product_uom_qty
                    })
                    stock_picking.button_validate()
                    self.write({
                        'supply_reception_id': stock_picking.id
                    })
            super(SaleOrder, self).action_confirm()

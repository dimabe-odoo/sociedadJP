from odoo import models, fields, api
import datetime


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    supply_dispatch_id = fields.Many2one('stock.picking', 'Movimiento de cilindros:')

    purchase_without_supply = fields.Boolean(string='Compra Como dato')

    sale_with_rent = fields.Boolean(string='Préstamo de cilindros')

    show_supply = fields.Boolean(string='Mostrar Despacho de insumo')

    have_supply = fields.Boolean(string='Tiene Insumos', compute='compute_have_supply')

    @api.onchange('move_ids_without_package')
    def compute_have_supply(self):
        for item in self:
            item.have_supply = bool(item.move_ids_without_package.mapped('product_id').mapped('supply_id'))

    def button_validate(self):
        for item in self:
            raise models.ValidationError(item.purchase_id)
            message = ''
            picking_id = 0
            location_dest_id = 0
            location_id = 0
            values = {}
            if item.picking_type_code == 'outgoing':
                if item.sale_id.loan_supply:
                    reception_loan = self.env['stock.picking'].create({
                        'name': 'LEND/' + item.name,
                        'picking_type_code': 'incoming',
                        'picking_type_id': self.env['stock.picking.type'].search(
                            [('warehouse_id.id', '=', item.picking_type_id.warehouse_id.id),
                             ('sequence_code', '=', 'IN')]).id,
                        'location_id': self.env['stock.location'].search([('name', '=', 'Customers')]).id,
                        'location_dest_id': self.env['stock.warehouse'].search(
                            [('id', '=', item.picking_type_id.warehouse_id.id)]).loan_location_id.id,
                        'state': 'assigned',
                        'date_done': datetime.datetime.now(),
                        'origin': item.origin,
                        'partner_id': item.partner_id.id
                    })
                    picking_id = reception_loan.id
                    location_id = reception_loan.location_id.id
                    location_dest_id = reception_loan.location_dest_id.id
                else:
                    reception = self.env['stock.picking'].create({
                        'name': 'IN/' + item.name,
                        'picking_type_code': 'incoming',
                        'picking_type_id': self.env['stock.picking.type'].search(
                            [('warehouse_id.id', '=', item.picking_type_id.warehouse_id.id),
                             ('sequence_code', '=', 'IN')]).id,
                        'location_id': self.env['stock.location'].search([('name', '=', 'Customers')]).id,
                        'location_dest_id': self.env['stock.warehouse'].search(
                            [('id', '=', item.picking_type_id.warehouse_id.id)]).lot_stock_id.id,
                        'state': 'assigned',
                        'date_done': datetime.datetime.now(),
                        'origin': item.origin,
                        'partner_id': item.partner_id.id
                    })
                    picking_id = reception.id
                    location_id = reception.location_id.id
                    location_dest_id = reception.location_dest_id.id
            if item.picking_type_code == 'incoming':
                dispatch = self.env['stock.picking'].create({
                    'name': 'OUT/' + item.name,
                    'picking_type_code': 'outgoing',
                    'picking_type_id': self.env['stock.picking.type'].search(
                        [('warehouse_id.id', '=', item.picking_type_id.warehouse_id.id),
                         ('sequence_code', '=', 'OUT')]).id,
                    'location_id': self.env['stock.location'].search([('name', '=', 'Vendors')]).id,
                    'location_dest_id': self.env['stock.warehouse'].search(
                        [('id', '=', item.picking_type_id.warehouse_id.id)]).lot_stock_id.id,
                    'state': 'assigned',
                    'date_done': datetime.datetime.now(),
                    'origin': item.origin,
                    'partner_id': item.partner_id.id
                })
                picking_id = dispatch.id
                location_id = dispatch.location_id.id
                location_dest_id = dispatch.location_dest_id.id
        for move in item.move_ids_without_package:
            if move.product_id.supply_id:
                quant = self.env['stock.quant'].search([('product_id.id', '=', move.product_id.supply_id.id),
                                                        ('location_id.id', '=', item.location_dest_id.id)])
                if quant.quantity < move.product_uom_qty and self.picking_type_code == 'incoming':
                    raise models.UserError('No tiene la cantidad necesaria de insumos {}'.format(
                        supply_id.display_name))
                if item.sale_id.loan_supply:
                    quantity = move.product_uom_qty - move.loan_supply
                else:
                    quantity = move.product_uom_qty - move.purchase_without_supply
                stock_move = self.env['stock.move'].create({
                    'picking_id': picking_id,
                    'name': 'MOVE',
                    'location_id': location_id,
                    'location_dest_id': location_dest_id,
                    'product_id': move.product_id.supply_id.id,
                    'date': datetime.datetime.now(),
                    'company_id': self.env.user.company_id.id,
                    'procure_method': 'make_to_stock',
                    'product_uom_qty': quantity,
                    'product_uom': move.product_id.supply_id.uom_id.id,
                    'date_expected': item.scheduled_date
                })
                self.env['stock.move.line'].create({
                    'company_id': stock_move.company_id.id,
                    'date': stock_move.date,
                    'location_id': stock_move.location_id.id,
                    'location_dest_id': stock_move.location_dest_id.id,
                    'product_uom_id': stock_move.product_uom.id,
                    'product_id': stock_move.product_id.id,
                    'qty_done': stock_move.product_uom_qty
                })
            item.write({
                'supply_dispatch_id': picking_id,
                'show_supply': True,
                'purchase_without_supply': False
            })
        res = super(StockPicking, self).button_validate()
        return res

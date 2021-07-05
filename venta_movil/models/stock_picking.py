import datetime

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    supply_dispatch_id = fields.Many2one('stock.picking', 'Movimiento de insumos:')

    purchase_without_supply = fields.Boolean(string='Compra Como dato')

    sale_with_rent = fields.Boolean(string='Préstamo de cilindros')

    show_supply = fields.Boolean(string='Mostrar Despacho de insumo')

    have_supply = fields.Boolean(string='Tiene Insumos', compute='compute_have_supply')

    loan_reception_id = fields.Many2one('stock.picking', 'Prestamo de insumos')

    @api.onchange('move_ids_without_package')
    def compute_have_supply(self):
        for item in self:
            item.have_supply = bool(item.move_ids_without_package.mapped('product_id').mapped('supply_id'))

    def button_validate(self):
        for item in self:
            if item.origin and 'Entrada' not in item.origin or 'Salida' not in item.origin and not item.supply_dispatch_id:
                if item.sale_id:
                    if item.move_ids_without_package.mapped('product_id').mapped('supply_id'):
                        if item.sale_id.loan_supply:
                            loan_reception = self.env['stock.picking'].create({
                                'name': f'LOAN{item.name}',
                                'picking_type_id': item.picking_type_id.warehouse_id.in_type_id.id,
                                'location_id': item.parent_id.property_stock_supplier.id,
                                'location_dest_id': item.picking_type_id.warehouse_id.loan_location_id.id,
                                'origin': f'Prestamo de {item.origin}',
                                'partner_id': item.partner_id.id
                            })
                            item.write({
                                'loan_reception_id': loan_reception.id,
                                'show_supply': True
                            })
                        if item.move_ids_without_package.filtered(lambda a: (a.loan_supply - a.product_uom_qty) != 0):
                            reception = self.env['stock.picking'].create({
                                'name': f'IN{item.name}',
                                'picking_type_id': item.picking_type_id.warehouse_id.in_type_id.id,
                                'location_id': item.partner_id.property_stock_supplier.id,
                                'location_dest_id': item.picking_type_id.warehouse_id.lot_stock_id.id,
                                'state': 'assigned',
                                'origin': f'Entrada de {item.origin}',
                                'partner_id': item.partner_id.id
                            })
                            item.write({
                                'supply_dispatch_id': reception.id,
                                'show_supply': True
                            })
                        for move in item.move_ids_without_package:
                            if move.product_id.supply_id:
                                quant = self.env['stock.quant'].search(
                                    [('product_id.id', '=', move.product_id.supply_id.id),
                                     ('location_id.id', '=', item.location_id.id)])
                            if (move.product_uom_qty - move.loan_supply) != 0:
                                qty = move.product_uom_qty
                                stock_move = self.env['stock.move'].create({
                                    'picking_id': reception.id,
                                    'name': move.product_id.supply_id.display_name,
                                    'location_id': reception.location_id.id,
                                    'location_dest_id': reception.location_dest_id.id,
                                    'product_id': move.product_id.supply_id.id,
                                    'date': datetime.date.today(),
                                    'procure_method': 'make_to_stock',
                                    'product_uom_qty': qty,
                                    'product_uom': move.product_id.supply_id.uom_id.id,
                                    'date_expected': item.scheduled_date
                                })
                            if item.sale_id.loan_supply:
                                qty = move.product_uom_qty - move.loan_supply
                                stock_move = self.env['stock.move'].create({
                                    'picking_id': loan_reception.id,
                                    'name': 'MOVE/' + item.name,
                                    'location_id': loan_reception.location_id.id,
                                    'location_dest_id': loan_reception.location_dest_id.id,
                                    'product_id': move.product_id.supply_id.id,
                                    'date': datetime.datetime.now(),
                                    'company_id': self.env.user.company_id.id,
                                    'procure_method': 'make_to_stock',
                                    'product_uom_qty': move.loan_supply,
                                    'product_uom': move.product_id.supply_id.uom_id.id,
                                    'date_expected': item.scheduled_date
                                })
                        item.supply_dispatch_id.action_confirm()
                        item.supply_dispatch_id.action_assign()
                        for line in item.supply_dispatch_id.move_line_ids_without_package:
                            line.write({
                                'qty_done': line.product_uom_qty
                            })
                        item.supply_dispatch_id.button_validate()
                        if item.loan_reception_id:
                            item.loan_reception_id.action_confirm()
                            item.loan_reception_id.action_assign()
                            for line in item.loan_reception_id.move_line_ids_without_package:
                                line.write({
                                    'qty_done': line.product_uom_qty
                                })
                            item.loan_reception_id.button_validate()
                else:
                    if item.move_ids_without_package.filtered(lambda a: a.product_id.supply_id):
                        dispatch = self.env['stock.picking'].create({
                            'name': f'OUT/{item.name}',
                            'picking_type_id': item.picking_type_id.warehouse_id.out_type_id.id,
                            'location_dest_id': item.picking_type_id.warehouse_id.lot_stock_id.id,
                            'location_id': item.partner_id.property_stock_customer.id,
                            'origin': f'Salida de {self.name}',
                            'partner_id': item.partner_id.id,
                        })
                        for move in item.move_ids_without_package:
                            if move.product_id.supply_id:
                                quant = self.env['stock.quant'].search(
                                    [('product_id.id', '=', move.product_id.supply_id.id),
                                     ('location_id.id', '=', item.location_dest_id.id)])
                                if quant.quantity < move.product_uom_qty:
                                    raise models.ValidationError(
                                        f'No tiene cantidad necesaria de insumos {move.product_id.supply_id.display_name}')
                            qty = move.product_uom_qty
                            stock_move = self.env['stock.move'].create({
                                'picking_id': dispatch.id,
                                'name': move.product_id.supply_id.display_name,
                                'location_id': dispatch.location_dest_id.id,
                                'location_dest_id': dispatch.location_id.id,
                                'product_id': move.product_id.supply_id.id,
                                'date': datetime.date.today(),
                                'procure_method': 'make_to_stock',
                                'product_uom_qty': qty,
                                'product_uom': move.product_id.supply_id.uom_id.id,
                                'date_expected': item.scheduled_date
                            })
                        item.write({
                            'supply_dispatch_id': dispatch.id,
                            'show_supply': True
                        })
                        item.supply_dispatch_id.action_confirm()
                        item.supply_dispatch_id.action_assign()
                        for line in item.supply_dispatch_id.move_line_ids_without_package:
                            line.write({
                                'qty_done': line.product_uom_qty
                            })
                        item.supply_dispatch_id.button_validate()
            return super(StockPicking, self).button_validate()

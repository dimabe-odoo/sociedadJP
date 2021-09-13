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
        res = super(StockPicking, self).button_validate()
        if self.state == 'done' and self.picking_type_id.sequence_code != 'INT':
            if not self.supply_dispatch_id or not self.loan_reception_id:
                self.process_supply_movement()
        return res

    def process_supply_movement(self):
        if self.sale_id:
            if self.move_ids_without_package.mapped('product_id').mapped('supply_id'):
                if self.sale_id.loan_supply:
                    loan_reception = self.env['stock.picking'].create({
                        'name': f'LOAN{self.name}',
                        'picking_type_id': self.picking_type_id.warehouse_id.in_type_id.id,
                        'location_id': self.parent_id.property_stock_supplier.id,
                        'location_dest_id': self.picking_type_id.warehouse_id.loan_location_id.id,
                        'origin': f'Prestamo de {self.origin}',
                        'partner_id': self.partner_id.id
                    })
                    self.write({
                        'loan_reception_id': loan_reception.id,
                        'show_supply': True
                    })
                if self.move_ids_without_package.filtered(lambda a: (a.loan_supply - a.product_uom_qty) != 0):
                    reception = self.env['stock.picking'].create({
                        'name': f'IN{self.name}',
                        'picking_type_id': self.picking_type_id.warehouse_id.in_type_id.id,
                        'location_id': self.partner_id.property_stock_supplier.id,
                        'location_dest_id': self.picking_type_id.warehouse_id.lot_stock_id.id,
                        'state': 'assigned',
                        'origin': f'Entrada de {self.origin}',
                        'partner_id': self.partner_id.id
                    })
                    self.write({
                        'supply_dispatch_id': reception.id,
                        'show_supply': True
                    })
                for move in self.move_ids_without_package:
                    if move.product_id.supply_id:
                        quant = self.env['stock.quant'].search(
                            [('product_id.id', '=', move.product_id.supply_id.id),
                             ('location_id.id', '=', self.location_id.id)])
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
                            'date_expected': self.scheduled_date
                        })
                    if self.sale_id.loan_supply:
                        qty = move.product_uom_qty - move.loan_supply
                        stock_move = self.env['stock.move'].create({
                            'picking_id': loan_reception.id,
                            'name': 'MOVE/' + self.name,
                            'location_id': loan_reception.location_id.id,
                            'location_dest_id': loan_reception.location_dest_id.id,
                            'product_id': move.product_id.supply_id.id,
                            'date': datetime.datetime.now(),
                            'company_id': self.env.user.company_id.id,
                            'procure_method': 'make_to_stock',
                            'product_uom_qty': move.loan_supply,
                            'product_uom': move.product_id.supply_id.uom_id.id,
                            'date_expected': self.scheduled_date
                        })
                self.supply_dispatch_id.action_confirm()
                self.supply_dispatch_id.action_assign()
                for line in self.supply_dispatch_id.move_line_ids_without_package:
                    line.write({
                        'qty_done': line.product_uom_qty
                    })
                self.supply_dispatch_id.button_validate()
                if self.loan_reception_id:
                    self.loan_reception_id.action_confirm()
                    self.loan_reception_id.action_assign()
                    for line in self.loan_reception_id.move_line_ids_without_package:
                        line.write({
                            'qty_done': line.product_uom_qty
                        })
                    self.loan_reception_id.button_validate()
        else:
            if self.move_ids_without_package.filtered(lambda a: a.product_id.supply_id):
                dispatch = self.env['stock.picking'].create({
                    'name': f'OUT/{self.name}',
                    'picking_type_id': self.picking_type_id.warehouse_id.out_type_id.id,
                    'location_dest_id': self.picking_type_id.warehouse_id.lot_stock_id.id,
                    'location_id': self.partner_id.property_stock_customer.id,
                    'origin': f'Salida de {self.name}',
                    'partner_id': self.partner_id.id,
                })
                for move in self.move_ids_without_package:
                    qty = move.product_uom_qty - move.purchase_without_supply if self.purchase_without_supply else move.product_uom_qty
                    if qty == 0:
                        continue
                    if move.product_id.supply_id:
                        quant = self.env['stock.quant'].search(
                            [('product_id.id', '=', move.product_id.supply_id.id),
                             ('location_id.id', '=', self.location_dest_id.id)])
                        if quant.quantity < qty:
                            raise models.ValidationError(
                                f'No tiene cantidad necesaria de insumos {move.product_id.supply_id.display_name}')
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
                        'date_expected': self.scheduled_date
                    })
                if qty != 0:
                    self.write({
                        'supply_dispatch_id': dispatch.id,
                        'show_supply': True
                    })
                    self.supply_dispatch_id.action_confirm()
                    self.supply_dispatch_id.action_assign()
                    for line in self.supply_dispatch_id.move_line_ids_without_package:
                        line.write({
                            'qty_done': line.product_uom_qty
                        })
                    self.supply_dispatch_id.button_validate()

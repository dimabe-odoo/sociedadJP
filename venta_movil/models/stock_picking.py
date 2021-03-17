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
            if item.picking_type_id.code not in ('outgoing', 'incoming'):
                return super(StockPicking, self).button_validate()
            elif item.origin:
                if "Entrada" in item.origin and "Salida" in item.origin or item.origin == '' or not item.origin:
                    return super(StockPicking, self).button_validate()
                elif item.sale_id:
                    if item.sale_id.with_delivery:
                        if item.move_ids_without_package.mapped('product_id').mappped('supply_id'):
                            if item.picking_type_id.code == 'outgoing':
                                if item.sale_id.loan_supply:
                                    loan_recepction_id = self.env['stock.picking'].create({
                                        'name': f'LOAN/{self.name}',
                                        'picking_type_id': self.picking_type_id.warehouse_id.in_type_id.id,
                                        'location_id': self.parent_id.property_stock_supplier.id,
                                        'location_dest_id': self.picking_type_id.warehouse_id.loan_location_id.id,
                                        'move_direct': 'direct',
                                        'origin': f'Entrada de {item.self.name}',
                                        'partner_id': self.partner_id.id
                                    })
                                    item.write({
                                        'loan_reception_id': loan_recepction_id.id,
                                        'have_supply': True
                                    })
                                if item.move_ids_without_package.filtered(
                                        lambda a: (a.loan_supply - a.product_uom_qty) != 0):
                                    reception = self.env['stock.picking'].create({
                                        'name': f'IN/{item.name}',
                                        'picking_type_id': self.picking_type_id.warehouse_id.in_type_id.id,
                                        'location_id': self.partner_id.property_stock_supplier.id,
                                        'location_dest_id': self.env['stock.warehouse'].search(
                                            [('id', '=', item.picking_type_id.warehouse_id.id)]).lot_stock_id.id,
                                        'state': 'assigned',
                                        'move_direct': 'direct',
                                        'origin': 'Entrada de ' + item.origin,
                                        'partner_id': item.partner_id.id
                                    })
                                    self.write({
                                        'supply_dispatch_id': reception.id,
                                        'have_supply': True
                                    })
                                for move in item.move_ids_without_package:
                                    if move.product_id.supply_id:
                                        quant = self.env['stock.quant'].search(
                                            [('product_id.id', '=', move.product_id.supply_id.id),
                                             ('location_id', '=', item.location_dest_id.id)])
                                        if quant.quantity < move.product_uom_qty and self.picking_type_id.code == 'incoming':
                                            raise models.UserError(
                                                f'No tiene la cantidad necesaria de insumos {move.product_id.supply_id.display_name}')
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
                                        item.supply_dispatch_id.button_validate()
                                        if item.sale_id.loan_supply:
                                            qty = move.product_uom_qty - move.loan_supply
                                            stock_move = self.env['stock.move'].create({
                                                'picking_id': loan_recepction_id.id,
                                                'name': 'MOVE/' + item.name,
                                                'location_id': loan_recepction_id.location_id.id,
                                                'location_dest_id': loan_recepction_id.location_dest_id.id,
                                                'product_id': move.product_id.supply_id.id,
                                                'date': datetime.datetime.now(),
                                                'company_id': self.env.user.company_id.id,
                                                'procure_method': 'make_to_stock',
                                                'product_uom_qty': move.loan_supply,
                                                'product_uom': move.product_id.supply_id.uom_id.id,
                                                'date_expected': item.scheduled_date
                                            })
                                            item.loan_reception_id.button_validate()
                                return super(StockPicking, self).button_validate()
                            else:
                                reception = self.env['stock.picking'].create({
                                    'name': 'OUT/' + item.name,
                                    'picking_type_code': 'outgoing',
                                    'picking_type_id': self.env['stock.picking.type'].search(
                                        [('warehouse_id.id', '=', item.picking_type_id.warehouse_id.id),
                                         ('sequence_code', '=', 'OUT')]).id,
                                    'location_dest_id': self.env['stock.location'].search(
                                        [('name', '=', 'Vendors')]).id,
                                    'location_id': self.env['stock.warehouse'].search(
                                        [('id', '=', item.picking_type_id.warehouse_id.id)]).lot_stock_id.id,
                                    'state': 'assigned',
                                    'date_done': datetime.datetime.now(),
                                    'origin': 'Salida de ' + item.origin,
                                    'partner_id': item.partner_id.id
                                })
                                self.write({
                                    'supply_dispatch_id': reception.id,
                                    'have_supply': True
                                })
                                for move in item.move_ids_without_package:
                                    if move.product_id.supply_id:
                                        quant = self.env['stock.quant'].search(
                                            [('product_id.id', '=', move.product_id.supply_id.id),
                                             ('location_id.id', '=', item.location_dest_id.id)])
                                        if quant.quantity < move.product_uom_qty and self.picking_type_code == 'incoming':
                                            raise models.UserError(
                                                'No tiene la cantidad necesaria de insumos {}'.format(
                                                    move.product_id.supply_id.display_name))
                                        if (move.product_uom_qty - move.loan_supply) != 0:
                                            qty = move.product_uom_qty
                                            self.env['stock.move'].create({
                                                'picking_id': reception.id,
                                                'name': 'MOVE/' + item.name,
                                                'location_id': reception.location_id.id,
                                                'location_dest_id': reception.location_dest_id.id,
                                                'product_id': move.product_id.supply_id.id,
                                                'date': datetime.datetime.now(),
                                                'company_id': self.env.user.company_id.id,
                                                'procure_method': 'make_to_stock',
                                                'quantity_done': qty,
                                                'product_uom': move.product_id.supply_id.uom_id.id,
                                                'date_expected': item.scheduled_date
                                            })
                                item.supply_dispatch_id.button_validate()
                                return super(StockPicking, self).button_validate()
                    else:
                        return super(StockPicking, self).button_validate()

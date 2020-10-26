from odoo import models, fields, api
import datetime


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    supply_dispatch_id = fields.Many2one('stock.picking', 'Movimiento de insumos:')

    purchase_without_supply = fields.Boolean(string='Compra Como dato')

    sale_with_rent = fields.Boolean(string='Préstamo de cilindros')

    show_supply = fields.Boolean(string='Mostrar Despacho de insumo')

    have_supply = fields.Boolean(string='Tiene Insumos', compute='compute_have_supply')

    loan_reception_id = fields.Many2one('stock.picking','Prestamo de insumos')

    @api.onchange('move_ids_without_package')
    def compute_have_supply(self):
        for item in self:
            item.have_supply = bool(item.move_ids_without_package.mapped('product_id').mapped('supply_id'))

    def button_validate(self):
        for item in self:
            if ('Entrada' in item.origin) or ('Salida' in item.origin):
                return super(StockPicking,self).button_validate()
            if item.purchase_id or item.sale_id:

                if item.picking_type_code == 'outgoing':
                    raise models.ValidationError('Aca')
                    if item.sale_id.loan_supply:
                        loan_reception_id = self.env['stock.picking'].create({
                            'name': 'LOAN/{}'.format(self.name),
                            'picking_type_id': self.env['stock.picking.type'].search([
                                ('warehouse_id.id', '=', self.picking_type_id.warehouse_id.id),
                                ('sequence_code', '=', 'IN')
                            ]).id,
                            'location_id': self.env['stock.location'].search([('name', '=', 'Customers')]).id,
                            'location_dest_id': self.env['stock.warehouse'].search([
                                ('id', '=', self.picking_type_id.warehouse_id.id)
                            ]).loan_location_id.id,
                            'move_type': 'direct',
                            'picking_type_code': 'incoming',
                            'state': 'assigned',
                            'date_done': datetime.datetime.now(),
                            'company_id': self.env.user.company_id.id,
                            'origin': 'Entrada de {}'.format(self.name),
                            'partner_id': self.partner_id.id
                        })
                        self.write({
                            'loan_reception_id':loan_reception_id.id
                        })
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
                            'origin': 'Entrada de ' + item.origin,
                            'partner_id': item.partner_id.id
                        })
                        self.write({
                            'supply_dispatch_id': reception.id,
                            'have_supply' : True
                        })
                        for move in item.move_ids_without_package:
                            if move.product_id.supply_id:
                                quant = self.env['stock.quant'].search(
                                    [('product_id.id', '=', move.product_id.supply_id.id),
                                     ('location_id.id', '=', item.location_dest_id.id)])
                                if quant.quantity < move.product_uom_qty and self.picking_type_code == 'incoming':
                                    raise models.UserError('No tiene la cantidad necesaria de insumos {}'.format(
                                        move.product_id.supply_id.display_name))
                                if item.sale_id.loan_supply:
                                    qty = move.product_uom_qty - move.loan_supply
                                    self.env['stock.move'].create({
                                        'picking_id': loan_reception_id.id,
                                        'name': 'MOVE/' + item.name,
                                        'location_id': loan_reception_id.location_id.id,
                                        'location_dest_id': loan_reception_id.location_dest_id.id,
                                        'product_id': move.product_id.supply_id.id,
                                        'date': datetime.datetime.now(),
                                        'company_id': self.env.user.company_id.id,
                                        'procure_method': 'make_to_stock',
                                        'quantity_done': move.loan_supply,
                                        'product_uom': move.product_id.supply_id.uom_id.id,
                                        'date_expected': item.scheduled_date
                                    })
                                    item.loan_reception_id.button_validate()
                                else:
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
                        'origin': 'Salida de ' + item.origin,
                        'partner_id': item.partner_id.id
                    })
                    for move in item.move_ids_without_package:
                        if move.product_id.supply_id:
                            quant = self.env['stock.quant'].search(
                                [('product_id.id', '=', move.product_id.supply_id.id),
                                 ('location_id.id', '=', item.location_dest_id.id)])
                            if quant.quantity < move.product_uom_qty and self.picking_type_code == 'incoming':
                                raise models.UserError('No tiene la cantidad necesaria de insumos {}'.format(
                                    move.product_id.supply_id.display_name))
                            quantity = move.product_uom_qty - move.purchase_without_supply
                            stock_move = self.env['stock.move'].create({
                                'picking_id': dispatch.id,
                                'name': 'MOVE/' + item.name,
                                'location_id': dispatch.location_id.id,
                                'location_dest_id': dispatch.location_dest_id.id,
                                'product_id': move.product_id.supply_id.id,
                                'date': datetime.datetime.now(),
                                'company_id': self.env.user.company_id.id,
                                'procure_method': 'make_to_stock',
                                'quantity_done': quantity,
                                'product_uom': move.product_id.supply_id.uom_id.id,
                                'date_expected': item.scheduled_date
                            })
                    item.write({
                            'supply_dispatch_id': dispatch.id,
                            'purchase_without_supply': True
                    })
                    return super(StockPicking, self).button_validate()

from odoo import models, fields, api
import datetime


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    supply_dispatch_id = fields.Many2one('stock.picking', 'Cilindros Despachados:')

    purchase_without_supply = fields.Boolean(string='Compra ComoDato')

    sale_with_rent = fields.Boolean(string='Préstamo de cilindros')

    show_supply = fields.Boolean(string='Mostrar Despacho de insumo', compute='compute_show_dipatch')

    def button_validate(self):
        if not self.origin or self.picking_type_code != 'internal':
            raise models.ValidationError('El movimiento no cuenta con un documento de referencia')
        if self.purchase_without_supply:
            res = super(StockPicking, self).button_validate()
            return res
        if self.sale_id and self.picking_type_code == 'outgoing':
            self.sale_id.supply_reception_id.button_validate()
        for stock_picking in self:
            message = ''
            stock_moves = []
            for move in stock_picking.move_ids_without_package:
                if move.product_id.supply_id:
                    supply_id = move.product_id.supply_id
                    quant = self.env['stock.quant'].search(
                        [('product_id', '=', supply_id.id),
                         ('location_id', '=', stock_picking.location_dest_id.id)])
                    if quant.quantity < move.product_uom_qty and self.picking_type_code == 'incoming':
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

            res = super(StockPicking, self).button_validate()
            if res:
                if stock_picking.picking_type_code == 'outgoing':
                    name = 'IN/{}'.format(stock_picking.name)
                    location = self.env['stock.location'].search([('name', '=', 'Customers')])
                    if stock_picking.sale_id.loan_supply:
                        location = self.env['stock.location'].search([('name', '=', 'Customers')])
                        loan = self.env['stock.warehouse'].search(
                            [('warehouse_id', '=', self.picking_type_id.warehouse_id.id)]).loan_location
                        dispatch = self.env['stock.picking'].create({
                            'name': name,
                            'picking_type_code': 'incoming',
                            'origin': stock_picking.origin,
                            'state': 'done',
                            'location_id': location.id,
                            'location_dest_id': loan.id,
                            'date_done': datetime.datetime.now(),
                            'picking_type_id': self.env['stock.picking.type'].search(
                                [('default_location_src_id', '=', stock_picking.location_dest_id.id),
                                 ('sequence_code', '=', 'IN')]).id,
                            'partner_id': stock_picking.partner_id.id
                        })
                    else:
                        dispatch = self.env['stock.picking'].create({
                            'name': name,
                            'picking_type_code': 'incoming',
                            'origin': stock_picking.origin,
                            'state': 'done',
                            'location_id': location.id,
                            'location_dest_id': stock_picking.location_id.id,
                            'date_done': datetime.datetime.now(),
                            'picking_type_id': self.env['stock.picking.type'].search(
                                [('default_location_src_id', '=', stock_picking.location_dest_id.id),
                                 ('sequence_code', '=', 'IN')]).id,
                            'partner_id': stock_picking.partner_id.id
                        })
                if stock_picking.picking_type_code == 'incoming':
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
                    if self.picking_type_code == 'outgoing':
                        product_id = self.env['product.product'].search([('supply_id.id', '=', move.product_id.id)])
                        if product_id:
                            move = self.env['stock.move'].create({
                                'name': dispatch.name,
                                'picking_id': dispatch.id,
                                'company_id': stock['company_id'],
                                'date': stock['date'],
                                'location_id': location.id,
                                'location_dest_id': loan.id,
                                'state': 'done',
                                'product_id': product_id.id,
                                'product_uom': product_id.uom_id.id,
                                'product_uom_qty': stock['product_uom_qty']
                            })
                            self.env['stock.move.line'].create({
                                'move_id': move.id,
                                'picking_id': dispatch.id,
                                'company_id': stock['company_id'],
                                'date': stock['date'],
                                'state': 'done',
                                'location_id': stock['location_id'],
                                'product_id': product_id.id,
                                'product_uom_id': product_id.uom_id.id,
                                'qty_done': move.product_uom_qty,
                                'location_dest_id': move.location_dest_id.id,
                            })
                        else:
                            move = self.env['stock.move'].create({
                                'name': dispatch.name,
                                'picking_id': dispatch.id,
                                'company_id': stock['company_id'],
                                'date': stock['date'],
                                'location_id': location.id,
                                'location_dest_id': loan.id,
                                'state': 'done',
                                'product_id': stock['product_id'],
                                'product_uom': stock['product_uom'],
                                'product_uom_qty': stock['product_uom_qty']
                            })
                            self.env['stock.move.line'].create({
                                'move_id': move.id,
                                'picking_id': dispatch.id,
                                'company_id': stock['company_id'],
                                'date': stock['date'],
                                'state': 'done',
                                'location_id': stock['location_id'],
                                'product_id': stock['product_id'],
                                'product_uom_id': stock['product_uom'],
                                'qty_done': move.product_uom_qty,
                                'location_dest_id': move.location_dest_id.id,
                            })
                    if picking_type_code == 'incoming':
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
                        self.env['stock.move.line'].create({
                            'move_id': move.id,
                            'picking_id': dispatch.id,
                            'company_id': stock['company_id'],
                            'date': stock['date'],
                            'state': 'done',
                            'location_id': stock['location_id'],
                            'product_id': stock['product_id'],
                            'product_uom_id': stock['product_uom'],
                            'qty_done': move.product_uom_qty,
                            'location_dest_id': move.location_dest_id.id,
                        })
                stock_picking.write({
                    'supply_dispatch_id': dispatch.id
                })
            return res

    @api.onchange('supply_dispatch_id')
    def compute_show_dipatch(self):
        self.show_supply = self.supply_dispatch_id and self.picking_type_code == 'incoming'

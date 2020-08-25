from odoo import models, fields, api
import datetime


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    supply_dispatch_id = fields.Many2one('stock.picking', 'Cilindros Despachados:')

    purchase_without_supply = fields.Boolean(string='Compra Como dato')

    sale_with_rent = fields.Boolean(string='Préstamo de cilindros')

    show_supply = fields.Boolean(string='Mostrar Despacho de insumo')

    def button_validate(self):
        if not self.origin:
            raise models.ValidationError('El movimiento no cuenta con un documento de referencia')
        if self.purchase_without_supply:
            return super(StockPicking, self).button_validate()
        for item in self:
            message = ''
            product = []
            quantity = 0
            for move in item.move_line_ids_without_package:
                if move.product_id.supply_id:
                    quant = self.env['stock.quant'].search([('product_id.id', '=', move.product_id.supply_id.id),
                                                            ('location_id.id', '=', item.location_dest_id.id)])
                    product = move
                    if quant.quantity < move.product_uom_qty and self.picking_type_code == 'incoming':
                        raise models.UserError('No tiene la cantidad necesaria de insumos {}'.format(
                            supply_id.display_name))
            res = super(StockPicking, self).button_validate()
            if res:
                if item.picking_type_code == 'outgoing':
                    if item.sale_id.loan_supply:
                        dispatch = self.env['stock.picking'].create({
                            'name': 'IN/' + item.name,
                            'picking_type_code': 'incoming',
                            'picking_type_id': self.env['stock.picking.type'].search(
                                [('warehouse_id.id', '=', item.picking_type_id.warehouse_id.id), ('sequence_code', '=', 'OUT')]),
                            'location_id': self.env['stock.location'].search([('name', '=', 'Customers')]),
                            'location_dest_id': self.env['stock.warehouse'].search(
                                [('id', '=', item.picking_type_id.warehouse_id.id)]).loan_location.id,
                            'state': 'done',
                            'date_done': datetime.datetime.now(),
                            'origin': item.origin,
                            'partner_id': item.partner_id.id
                        })
                        stock_move = self.env['stock.move'].create({
                            'picking_id': dispatch.id,
                            'product_id': product.product_id.id,
                            'product_uom': product.product_id.uom_id,
                            'product_uom_qty': product.product_uom_qty,
                            'state': 'confirmed',
                            'location_id': dispatch.location_id.id,
                            'location_dest_id': dispatch.location_dest_id.id,
                            'date': datetime.datetime.now(),
                            'company_id': self.env.user.company_id.id
                        })
                        self.env['stock.move.line'].create({
                            'picking_id': stock_move.picking_id.id,
                            'move_id': stock_move.id,
                            'product_id': stock_move.product_id.id,
                            'product_uom_id': stock_m.product_uom.id,
                            'qty_done': stock_move.product_uom_qty,
                            'state': 'confirmed',
                            'company_id': stock_mov.company_id.id,
                            'location_id': stock_mov.location_id.id,
                            'location_dest_id': stock.location_dest_id.id
                        })
                    else:
                        dispatch = self.env['stock.picking'].create({
                            'name': 'IN/' + item.name,
                            'picking_type_code': 'incoming',
                            'picking_type_id': self.env['stock.picking.type'].search(
                                [('warehouse_id.id', '=', item.picking_type_id.warehouse_id.id), ('sequence_code', '=', 'IN')]),
                            'location_id': self.env['stock.location'].search([('name', '=', 'Customers')]),
                            'location_dest_id': self.env['stock.warehouse'].search(
                                [('id', '=', item.picking_type_id.warehouse_id.id)]).lot_stock_id.id,
                            'state': 'done',
                            'date_done': datetime.datetime.now(),
                            'origin': item.origin,
                            'partner_id': item.partner_id.id
                        })
                        stock_move = self.env['stock.move'].create({
                            'picking_id': dispatch.id,
                            'product_id': product.product_id.id,
                            'product_uom': product.product_id.uom_id,
                            'product_uom_qty': product.product_uom_qty,
                            'state': 'confirmed',
                            'location_id': dispatch.location_id.id,
                            'location_dest_id': dispatch.location_dest_id.id,
                            'date': datetime.datetime.now(),
                            'company_id': self.env.user.company_id.id
                        })
                        self.env['stock.move.line'].create({
                            'picking_id': stock_move.picking_id.id,
                            'move_id': stock_move.id,
                            'product_id': stock_move.product_id.id,
                            'product_uom_id': stock_m.product_uom.id,
                            'qty_done': stock_move.product_uom_qty,
                            'state': 'confirmed',
                            'company_id': stock_mov.company_id.id,
                            'location_id': stock_mov.location_id.id,
                            'location_dest_id': stock.location_dest_id.id
                        })
                if item.picking_type_code == 'incoming':
                    dispatch = self.env['stock.picking'].create({
                        'name': 'OUT/' + item.name,
                        'picking_type_code': 'outgoing',
                        'picking_type_id': self.env['stock.picking.type'].search(
                            [('warehouse_id.id', '=', item.picking_type_id.warehouse_id.id), ('sequence_code', '=', 'OUT')]),
                        'location_id': self.env['stock.location'].search([('name', '=', 'Vendors')]),
                        'location_dest_id': self.env['stock.warehouse'].search(
                            [('id', '=', item.picking_type_id.warehouse_id.id)]).lot_stock_id.id,
                        'state': 'done',
                        'date_done': datetime.datetime.now(),
                        'origin': item.origin,
                        'partner_id': item.partner_id.id
                    })
                    stock_move = self.env['stock.move'].create({
                        'picking_id': dispatch.id,
                        'product_id': product.product_id.id,
                        'product_uom': product.product_id.uom_id,
                        'product_uom_qty': product.product_uom_qty,
                        'state': 'confirmed',
                        'location_id': dispatch.location_id.id,
                        'location_dest_id': dispatch.location_dest_id.id,
                        'date': datetime.datetime.now(),
                        'company_id': self.env.user.company_id.id
                    })
                    self.env['stock.move.line'].create({
                        'picking_id': stock_move.picking_id.id,
                        'move_id': stock_move.id,
                        'product_id': stock_move.product_id.id,
                        'product_uom_id': stock_m.product_uom.id,
                        'qty_done': stock_move.product_uom_qty,
                        'state': 'confirmed',
                        'company_id': stock_mov.company_id.id,
                        'location_id': stock_mov.location_id.id,
                        'location_dest_id': stock.location_dest_id.id
                    })
            item.write({
                'supply_dispatch_id': dispatch.id,
                'show_supply': True
            })

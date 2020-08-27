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
            picking = self.env['stock.picking']
            quantity = 0
            values = {}
            if item.picking_type_code == 'incoming':
                values['name'] = 'OUT/' + item.name
                values['picking_type_code'] = 'outgoing'
                values['picking_type_id'] = self.env['stock.picking.type'].search(
                    [('warehouse_id.id', '=', item.picking_type_id.warehouse_id.id), ('sequence_code', '=', 'OUT')]).id
                values['location_dest_id'] = self.env['stock.location'].search([('name', '=', 'Customers')]).id
            if item.picking_type_code == 'outgoing':
                values['name'] = 'IN/' + item.name
                values['picking_type_code'] = 'incoming'
                values['picking_type_id'] = self.env['stock.picking.type'].search(
                    [('warehouse_id.id', '=', item.picking_type_id.warehouse_id.id), ('sequence_code', '=', 'IN')]).id
                values['location_dest_id'] = self.env['stock.location'].search([('name', '=', 'Vendors')]).id
            values['state'] = 'assigned'
            values['date_done'] = datetime.datetime.now()
            values['origin'] = item.origin
            values['partner_id'] = item.partner_id.id
            raise models.ValidationError('{},{}'.format(values.keys(),values.values()))
            picking.create(values)
            for move in item.move_ids_without_package:
                if move.product_id.supply_id:
                    quant = self.env['stock.quant'].search([('product_id.id', '=', move.product_id.supply_id.id),
                                                            ('location_id.id', '=', item.location_dest_id.id)])
                    if quant.quantity < move.product_uom_qty and self.picking_type_code == 'incoming':
                        raise models.UserError('No tiene la cantidad necesaria de insumos {}'.format(
                            supply_id.display_name))
                    stock_move = self.env['stock.move'].create({
                        'picking_id': picking.id,
                        'name': 'MOVE',
                        'location_id': picking.location_id.id,
                        'location_dest_id': picking.location_dest_id.id,
                        'product_id': move.product_id.supply_id.id,
                        'date': datetime.datetime.now(),
                        'company_id': self.env.user.company_id.id,
                        'procure_method': 'make_to_stock',
                        'product_uom_qty': move.product_uom_qty - move.purchase_without_supply,
                        'product_uom': move.product_id.supply_id.uom_id.id,
                        'date_expected': item.scheduled_date
                    })
                    self.env['stock.move.line'].create({
                        'company_id':stock_move.company_id.id,
                        'date':stock_move.date,
                        'location_id':stock_move.location_id.id,
                        'location_dest_id':stock_move.location_dest_id.id,
                        'product_uom_id':stock_move.product_uom_id.id,
                        'product_id': stock_move.product_id.id,
                        'product_uom_qty':stock_move.product_uom_qty
                    })
                else:
                    continue
            item.write({
                'supply_dispatch_id': picking.id,
                'show_supply': True
            })
            res = super(StockPicking, self).button_validate()
            return res

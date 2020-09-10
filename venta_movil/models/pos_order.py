from odoo import fields, models, api
import datetime


class PosOrder(models.Model):
    _inherit = 'pos.order'

    supply_reception_id = fields.Many2one('stock.picking', 'Recepcion de Insumos')

    loan_supply = fields.Integer()
    
    @api.model
    def create(self,values):
        models._logger.error('{},{}'.format(values.keys(),values.values()))
        return super(PosOrder, self).create(values)

    def create_picking(self):
        res = super(PosOrder, self).create_picking()
        if self.lines.filtered(lambda l: l.product_id.supply_id):
            reception_id = self.env['stock.picking'].create({
                'name': 'POS/IN/{}'.format(self.name),
                'picking_type_id': self.env['stock.picking.type'].search(
                    [('warehouse_id.id', '=', self.picking_type_id.warehouse_id.id), ('sequence_code', '=', 'OUT')]).id,
                'location_id': self.env['stock.location'].search([('name', '=', 'Customers')]).id,
                'location_dest_id': self.location_id.id,
                'move_type': 'direct',
                'picking_type_code': 'incoming',
                'state': 'assigned',
                'date_done': datetime.datetime.now(),
                'company_id': self.env.user.company_id.id,
                'origin': 'Entrada de {}'.format(self.name),
                'partner_id': self.partner_id.id
            })
            self.write({
                'supply_reception_id': reception_id.id,
            })
        else:
            return res
        for line in self.lines:
            if line.product_id.supply_id:
                stock_move = self.env['stock.move'].create({
                    'name': reception_id.name,
                    'picking_id': reception_id.id,
                    'location_id': reception_id.location_id.id,
                    'location_dest_id': reception_id.location_dest_id.id,
                    'product_id': line.product_id.supply_id.id,
                    'date': datetime.datetime.now(),
                    'company_id': reception_id.company_id.id,
                    'procure_method': 'make_to_stock',
                    'quantity_done': line.qty,
                    'product_uom': line.product_id.supply_id.uom_id.id,
                })
                self.env['stock.move.line'].create({
                    'move_id': stock_move.id,
                    'company_id': stock_move.company_id.id,
                    'date': stock_move.date,
                    'location_id': stock_move.location_id.id,
                    'location_dest_id': stock_move.location_dest_id.id,
                    'product_id': stock_move.product_id.id,
                    'product_uom_id': stock_move.product_uom.id,
                    'qty_done': stock_move.quantity_done
                })
                reception_id.button_validate()
            else:
                continue
        return res

    @api.model
    def _order_fields(self, ui_order):
        models._logger.error(ui_order)
        order_fields = super(PosOrder, self)._order_fields(ui_order)
        order_fields['loan_supply'] = ui_order['lines']['loan']
        return order_fields

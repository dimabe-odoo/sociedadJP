from odoo import fields, models, api
import datetime


class PosOrder(models.Model):
    _inherit = 'pos.order'

    supply_reception_id = fields.Many2one('stock.picking', 'Recepcion de insumos')

    loan_reception_id = fields.Many2one('stock.picking', 'Prestamo de insumos')

    is_loan = fields.Boolean()

    @api.model
    def create(self, values):
        models._logger.error('{},{}'.format(values.keys(), values.values()))
        return super(PosOrder, self).create(values)

    def create_picking(self):
        res = super(PosOrder, self).create_picking()
        if self.lines.filtered(lambda l: l.product_id.supply_id):
            if self.lines.filtered(lambda q: q.loan > 0):
                loan_id = self.env['stock.picking'].create({
                    'name': 'POS/LOAN/{}'.format(self.name),
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
                    'loan_reception_id':loan_id.id
                })
            if self.lines.filtered(lambda a : (a.loan - a.qty) != 0):
                reception_id = self.env['stock.picking'].create({
                    'name': 'POS/IN/{}'.format(self.name),
                    'picking_type_id': self.env['stock.picking.type'].search([
                        ('warehouse_id.id', '=', self.picking_type_id.warehouse_id.id),
                        ('sequence_code', '=', 'IN')
                    ]).id,
                    'location_id': self.env['stock.location'].search([('name', '=', 'Customers')]).id,
                    'location_dest_id': self.env['stock.warehouse'].search([
                        ('id', '=', self.picking_type_id.warehouse_id.id)
                    ]).lot_stock_id.id,
                    'move_type': 'direct',
                    'picking_type_code': 'incoming',
                    'state': 'assigned',
                    'date_done': datetime.datetime.now(),
                    'company_id': self.env.user.company_id.id,
                    'origin': 'Entrada de {}'.format(self.name),
                    'partner_id': self.partner_id.id
                })
            self.write({
                'supply_reception_id': self.supply_reception_id.id
            })
            for line in self.lines:
                if line.product_id.supply_id:
                    if self.lines.filtered(lambda q: q.loan > 0):
                        loan_move = self.env['stock.move'].create({
                            'name': loan_id.name,
                            'picking_id': loan_id.id,
                            'location_id': loan_id.location_id.id,
                            'location_dest_id': loan_id.location_dest_id.id,
                            'product_id': line.product_id.supply_id.id,
                            'date': datetime.datetime.now(),
                            'company_id': loan_id.company_id.id,
                            'procure_method': 'make_to_stock',
                            'state':'assigned',
                            'quantity_done': line.loan,
                            'product_uom': line.product_id.supply_id.uom_id.id
                        })
                    if line.loan != 0:
                        qty = (line.qty - line.loan)
                    else:
                        qty = line.qty
                    if (line.qty - line.loan) != 0:
                        stock_move = self.env['stock.move'].create({
                            'name': reception_id.name,
                            'picking_id': reception_id.id,
                            'location_id': reception_id.location_id.id,
                            'location_dest_id': reception_id.location_dest_id.id,
                            'product_id': line.product_id.supply_id.id,
                            'date': datetime.datetime.now(),
                            'state': 'assigned',
                            'company_id': reception_id.company_id.id,
                            'procure_method': 'make_to_stock',
                            'quantity_done': qty,
                            'product_uom': line.product_id.supply_id.uom_id.id,
                        })
                    self.write({
                        'supply_reception_id':reception_id.id
                    })
                    self.supply_reception_id.button_validate()
                else:
                    continue
            if self.lines.filtered(lambda q: q.loan > 0):
                self.loan_reception_id.button_validate()
            self.supply_reception_id.button_validate()

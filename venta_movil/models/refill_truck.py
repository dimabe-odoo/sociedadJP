from odoo import fields, models


class RefillTruck(models.TransientModel):
    _name = 'refill.truck'

    warehouse_id = fields.Many2one('stock.warehouse', 'Bodega')

    truck_id = fields.Many2one('stock.location', 'Camion')

    truck_ids = fields.Many2many('stock.location', related='warehouse_id.truck_ids')

    def select(self):
        stock = self.env['stock.picking'].create({
            'partner_id': self.env.user_id.partner_id.id,

        })

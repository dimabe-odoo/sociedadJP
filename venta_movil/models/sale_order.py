from odoo import fields, models, api
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    loan_supply = fields.Boolean('¿Es prestamo de cilindro?')

    supply_reception_id = fields.Many2one('stock.picking', 'Entrada de insumo')

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.loan_supply:
            self.picking_ids.write({
                'loan_supply': True,
                'location_dest_id': self.warehouse_id.loan_location.id
            })
        return res

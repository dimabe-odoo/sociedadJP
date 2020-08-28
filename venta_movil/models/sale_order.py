from odoo import fields, models, api
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    loan_supply = fields.Boolean('¿Es prestamo de cilindro?')

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.loan_supply:
            for pick in self.picking_ids:
                pick.write({
                    'sale_with_rent': True
                })
        return res

from odoo import fields, models, api
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    loan_supply = fields.Boolean('¿Es prestamo de cilindro?')

    with_delivery = fields.Boolean('Despacho a Domicilio')

    origin = fields.Many2one('mobile.sale.order','Origen')

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.loan_supply:
            for pick in self.picking_ids:
                pick.write({
                    'sale_with_rent': True
                })
        return res

    def assign_location_id(self):
        raise models.ValidationError(self.user)

    def create(self, values):
        res = super(SaleOrder, self).create(values)

        discount_history = self.env['custom.discount.history'].create({
            'sale_id': values['id'],
            'customer_id': values['partner_id'],
            'date_discount': self.datetime.now()
        })

        return res

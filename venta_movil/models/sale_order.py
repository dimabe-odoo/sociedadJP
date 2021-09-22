from odoo import fields, models, api
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _default_warehouse_id(self):
        self.warehouse_id = None
        return None

    loan_supply = fields.Boolean('¿Es prestamo de cilindro?')

    with_delivery = fields.Boolean('Despacho a Domicilio')

    origin = fields.Many2one('mobile.sale.order','Origen')

    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse',
        required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        default=_default_warehouse_id, check_company=True)


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


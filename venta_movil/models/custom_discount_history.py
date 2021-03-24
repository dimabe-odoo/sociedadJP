from odoo import fields, api

class CustomDiscountHistory(models.Model):

    _name = 'custom.discount.history'

    sale_id = fields.Many2one('sale.order', string="Pedido")

    customer_id = fields.Many2one('res.partner', string="Cliente")

    discount_amount = fields.Integer(string="Monto Descuento", compute="_compute_discount_amount")

    date_discount = fields.Datetime(string="Fecha del Descuento")

    def _compute_discount_amount(self):
        print('')
from odoo import fields , models, api

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    loan = fields.Integer('Prestamo')
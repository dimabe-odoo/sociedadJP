from odoo import fields , models, api

class PosOrderLine(models.Models):
    _inherit = 'pos.order.line'

    loan_qty = fields.Float('Prestamo')
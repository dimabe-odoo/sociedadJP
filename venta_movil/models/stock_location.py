from odoo import fields, models, api


class StockLocation (models.Model):
    _inherit = 'stock.location'

    loan_location = fields.Boolean('¿Es ubicacion de prestamo?')
    



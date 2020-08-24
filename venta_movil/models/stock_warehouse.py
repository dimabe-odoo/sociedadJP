from odoo import fields, models, api


class StockWarehouse (models.Model):
    _inherit = 'stock.warehouse'

    loan_location_id = fields.Many2one('stock.location','Ubicacion de Prestamo')
    



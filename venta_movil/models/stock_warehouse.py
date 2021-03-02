from odoo import fields, models, api


class StockWarehouse (models.Model):
    _inherit = 'stock.warehouse'

    loan_location_id = fields.Many2one('stock.location','Ubicacion de Prestamo')
    
    truck_ids = fields.Many2many('stock.location',domain=[('is_truck','=',True)],string="Camiones")


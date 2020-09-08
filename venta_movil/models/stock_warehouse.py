from odoo import fields, models, api


class StockWarehouse (models.Model):
    _inherit = 'stock.warehouse'

    loan_location_id = fields.Many2one('stock.location','Ubicacion de Prestamo')

    is_truck = fields.Boolean('¿Es camion?')

    user_id = field.Many2one('res.user')


    



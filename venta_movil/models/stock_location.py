from odoo import fields, models, api


class StockLocation (models.Model):
    _inherit = 'stock.location'

    loan_location = fields.Boolean('¿Es ubicacion de prestamo?')

    is_truck = fields.Boolean('¿Es Camion?')

    user_id = fields.Many2one('res.users')


    @api.onchange('is_truck')
    def onchange_istruck(self):
        if self.is_truck:
            res = {
                'invisible':{
                    'user_id':{
                        1
                    }
                }
            }
        else:
            res = {
                'invisible': {
                    'user_id': {
                        1
                    }
                }
            }


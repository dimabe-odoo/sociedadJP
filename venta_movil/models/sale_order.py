from odoo import fields, models, api


class ModelName (models.Model):
    _inherit = 'sale.order'

    loan_supply = fields.Boolean('Prestamo de Cilindro')


    



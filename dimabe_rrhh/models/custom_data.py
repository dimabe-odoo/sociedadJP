from odoo import models, fields

class CustomData(models.Model):
    _name = 'custom.data'

    name = fields.Char('Nombre')

    value = fields.Float('Valor')

    data_type_id = fields.Many2one('custom.data.type','Tipo')

from odoo import models,fields

class CustomBenefitsRRHH(models.Model):
    _name = 'custom.benefits.rrhh'

    code = fields.Char('Codigo',required=True)

    name = fields.Char('Nombre',required=True)

    data_type_id = fields.Many2one(
        'custom.data.type',
        string='Tipo de Dato',
        )
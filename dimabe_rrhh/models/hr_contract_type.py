from odoo import models, fields

class HrContractType(models.Model):
    _inherit = 'hr.contract.type'

    code = fields.Char('Codigo')

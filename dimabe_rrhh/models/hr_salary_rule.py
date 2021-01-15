from odoo import models,fields,api

class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    is_bonus = fields.Boolean('Es Bono')

    @api.onchange('is_bonus')
    def onchange_method(self):
        raise models.ValidationError(self.code)

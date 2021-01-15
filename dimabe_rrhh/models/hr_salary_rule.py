from odoo import models,fields,api

class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    is_bonus = fields.Boolean('Es Bono')

    @api.onchange('is_bonus')
    def onchange_method(self):
        if not self.code:
            raise models.UserError('No pude definir un bono sin definir el codigo primero')
        if self.is_bonus:
            self.write({
                'condition_select':'python',
                'condition_python':f'result = (inputs.{self.code} and inputs.{self.code}.amount > 0)',
                'amount_select':'python',
                'amount_python_compute':f'result = inputs.{self.code}.amount'
            })

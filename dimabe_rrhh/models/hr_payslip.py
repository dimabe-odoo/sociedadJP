from odoo import models, fields, api


class HrPaySlip(models.Model):
    _inherit = 'hr.payslip'

    indicator_id = fields.Many2one('custom.indicators', string='Indicadores')

    salary_id = fields.Many2one('hr.salary.rule', 'Agregar Entrada')

    def add(self):
        for item in self:
            if item.salary_id:
                self.env['hr.payslip.input'].create({
                    'name': item.salary_id.name,
                    'code': item.salary_id.code,
                    'contract_id': item.contract_id.id,
                    'payslip_id': item.id
                })
            item.salary_id = None
    
    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        res = super(HrPaySlip, self).get_worked_day_lines(contracts, date_from, date_to)
        raise models.ValidationError('Test boton calcular hoja')
        return res

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
    
    def onchange_employee(self):
        for item in self:
            codes = []
            if self.employee_id:
                print('')
                #for line in item.worked_days_line_ids:
                #    if line.code not in codes:
                #        codes.append(line.code)
                #if 'WORK100' not in codes:
                #    self.env['hr.payslip.worked_days'].create({
                #        'work_entry_type_id': 1,
                #        'payslip_id': 1
                #    })
class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    @api.model
    def create(self, vals):
        res = super(HrPayslipWorkedDays, self).create
        raise models.ValidationError(vals.keys())
        return res
        
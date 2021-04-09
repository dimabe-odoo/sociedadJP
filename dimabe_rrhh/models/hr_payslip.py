from odoo import models, fields, api


class HrPaySlip(models.Model):
    _inherit = 'hr.payslip'

    indicator_id = fields.Many2one('custom.indicators', string='Indicadores')

    salary_id = fields.Many2one('hr.salary.rule', 'Agregar Entrada')

    def add(self):
        for item in self:
            if item.salary_id:
                type_id = self.env['hr.payslip.input.type'].search([('code','=',item.salary_id.code)])
                if type_id:
                    self.env['hr.payslip.input'].create({
                        'name': item.salary_id.name,
                        'code': item.salary_id.code,
                        'contract_id': item.contract_id.id,
                        'payslip_id': item.id,
                        'input_type_id': type_id.id
                    })
                else:
                    raise models.ValidationError(f'No existe tipo {item.code}')
            item.salary_id = None
    
    @api.model
    def _get_worked_day_lines(self):
        res = super(HrPaySlip, self)._get_worked_day_lines()
        temp = 0 
        days = 0
        attendances = {}
        leaves = []
        if len(res) > 0:
            for line in res:
                if line.get('code') == 'WORK100':
                    attendances = line
                else:
                    leaves.append(line)
            for leave in leaves:
                temp += leave.get('number_of_days') or 0
        attendances['number_of_days'] = days
        attendances['work_entry_type_id'] = 1
        res = []
        res.append(attendances)
        res.extend(leaves)
        return res

    
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
    def _get_worked_day_lines(self):
        res = super(HrPaySlip, self)._get_worked_day_lines()
        temp = 0 
        days = 0
        attendances = {}
        leaves = []
        #raise models.ValidationError(len(res))
        for line in res:
            if line.get('code') == 'WORK100':
                attendances = line
            else:
                leaves.append(line)
        for leave in leaves:
            temp += leave.get('number_of_days') or 0

        #Dias laborados reales para calcular la semana corrida
        
        #effective = attendances.copy()
        #effective.update({
        #    'name': _("Dias de trabajo efectivos"),
        #    'sequence': 2,
        #    'code': 'EFF100',
        #})
        # En el caso de que se trabajen menos de 5 días tomaremos los dias trabajados en los demás casos 30 días - las faltas
        # Estos casos siempre se podrán modificar manualmente directamente en la nomina.
        # Originalmente este dato se toma dependiendo de los dias del mes y no de 30 dias
        # TODO debemos saltar las vacaciones, es decir, las vacaciones no descuentan dias de trabajo. 

        #if (effective.get('number_of_days') or 0) < 5:
        #    dias = effective.get('number_of_days')
        #else:
        #    dias = 30 - temp
        attendances['number_of_days'] = days
        res = []
        res.append(attendances)
        #res.append(effective)
        res.extend(leaves)
        return res

    
from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_type_id = fields.Many2one('custom.data', 'Tipo de Empleado', domain=[('data_type_id', '=', 7)])

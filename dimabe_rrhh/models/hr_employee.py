from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_type_id = fields.Many2one('custom.data', 'Tipo de Empleado', domain=[('data_type_id', '=', 7)])

    first_name = fields.Char("Nombre")

    last_name = fields.Char("Apellido")

    middle_name = fields.Char("Segundo Nombre Name", help='Employees middle name')

    mothers_name = fields.Char("Segundo Apellido", help='Employees mothers name')

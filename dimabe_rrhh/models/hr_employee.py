from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_type_id = fields.Many2one('custom.employee.type', 'Tipo de Empleado')

    first_name = fields.Char("Nombre")

    last_name = fields.Char("Apellido")

    middle_name = fields.Char("Segundo Nombre", help='Employees middle name')

    mothers_name = fields.Char("Segundo Apellido", help='Employees mothers name')

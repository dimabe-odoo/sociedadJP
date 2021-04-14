from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_type_id = fields.Many2one('custom.employee.type', 'Tipo de Empleado')

    first_name = fields.Char("Nombre")

    last_name = fields.Char("Apellido")

    middle_name = fields.Char("Segundo Nombre", help='Employees middle name')

    mothers_name = fields.Char("Segundo Apellido", help='Employees mothers name')

    @api.model
    def _get_computed_name(self, last_name, first_name, last_name2=None, middle_name=None):
        names = []
        if first_name:
            names.append(first_name)
        if middle_name:
            names.append(middle_name)
        if last_name:
            names.append(last_name)
        if last_name2:
            names.append(last_name2)
        return " ".join(names)

    @api.onchange('first_name', 'mothers_name', 'middle_name', 'last_name')
    def get_name(self):
        if self.first_name and self.last_name:
            self.name = self._get_computed_name(self.last_name, self.first_name, self.mothers_name, self.middle_name)

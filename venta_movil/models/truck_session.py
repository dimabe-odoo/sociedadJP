from odoo import models, fields


class TruckSession(models.Model):
    _name = 'truck.session'

    login_datetime = fields.Datetime('Fecha de ultimo ingreso')

    user_id = fields.Many2one('res.users', 'Usuario')

    truck_id = fields.Many2one('stock.location', 'Camion', domain=[('is_truck', '=', True)])

    active = fields.Boolean('Activo')

    employee_id = fields.Many2one('hr.employee','Empleado')
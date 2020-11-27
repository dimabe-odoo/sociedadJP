import datetime

from odoo import models, fields


class TruckSession(models.Model):
    _name = 'truck.session'
    _rec_name = 'employee_id'

    login_datetime = fields.Datetime('Fecha de ultimo ingreso', default=datetime.datetime.now())

    user_id = fields.Many2one('res.users', 'Usuario')

    truck_id = fields.Many2one('stock.location', 'Camion', domain=[('is_truck', '=', True)])

    is_login = fields.Boolean('Activo', default=True)

    employee_id = fields.Many2one('hr.employee', 'Empleado')

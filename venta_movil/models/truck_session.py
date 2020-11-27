import datetime

from odoo import models, fields , api


class TruckSession(models.Model):
    _name = 'truck.session'
    _rec_name = 'employee_id'

    login_datetime = fields.Datetime('Fecha de inicio de sesion', default=datetime.datetime.now())

    user_id = fields.Many2one('res.users', 'Usuario',rel='employee_id.user_id')

    truck_id = fields.Many2one('stock.location', 'Camion', domain=[('is_truck', '=', True)],required=True)

    is_login = fields.Boolean('Activo', default=True)

    employee_id = fields.Many2one('hr.employee', 'Empleado',required=True)

    state = fields.Char()

    @api.model
    def create(self, values):
        truck = self.env['truck.session'].search([('truck_id','=',values['truck_id']),('employee_id','=',values['employee_id'])])
        if truck:
            if truck.is_login:
                raise models.ValidationError('Ya existe un sesion activa para este camion')
            elif not truck.is_login:
                truck.write({
                    'is_login': True
                    'login_datetime':datetime.datetime.now()
                })
            return null
        else:
            res = super(TruckSession, self).create(values)
            return res
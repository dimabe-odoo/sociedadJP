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

    @api.model
    def create(self, values):
        truck = self.env['truck.session'].search([('truck_id','=',values['truck_id'])])
        if truck:
            if truck.is_login:
                raise models.ValidationError('Ya existe un sesion activa para este camion')
            elif not truck.is_login:
                truck.write({
                    'is_login': True
                })
        else:
            values['state'] = 'draft'
            values['name'] = self.env['ir.sequence'].next_by_code('mobile.sale.order')
            res = super(TruckSession, self).create(values)
            return res
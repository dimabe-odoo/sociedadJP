import datetime

from odoo import models, fields , api


class TruckSession(models.Model):
    _name = 'truck.session'
    _rec_name = 'employee_id'

    login_datetime = fields.Datetime('Fecha de inicio de sesion', default=datetime.datetime.now())

    user_id = fields.Many2one('res.users', 'Usuario',rel='employee_id.user_id')

    truck_id = fields.Many2one('stock.location', 'Camion', domain=[('is_truck', '=', True)])

    is_login = fields.Boolean('Activo', default=True)

    employee_id = fields.Many2one('hr.employee', 'Empleado',required=True)

    state = fields.Char()

    is_present = fields.Boolean('Es Prestente',default=True)

    warehouse_id = fields.Many2one('stock.warehouse',"Bodega",compute="compute_warehouse_id")

    def compute_warehouse_id(self):
        for item in self:
            warehouse_id = self.env['stock.warehouse'].search([])
            for warehouse in warehouse_id:
                if item.truck_id in warehouse.truck_ids:
                    item.warehouse_id = warehouse
                    break
                else:
                    item.warehouse_id = None

    @api.model
    def create(self,values):
        if 'truck_id' in values.keys():
            truck = self.env['truck.session'].search(
                [('truck_id.id', '=', values['truck_id']), ('is_login', '=', True)])
            if truck:
                raise models.UserError('Hay existe un sesion activa')
            else:
                return super(TruckSession, self).create(values)
        else:
            return super(TruckSession, self).create(values)

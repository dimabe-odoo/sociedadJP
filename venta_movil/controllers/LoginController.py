from odoo import http
from odoo.http import request
from ..jwt_token import generate_token
import datetime
import logging


class LoginController(http.Controller):
    @http.route('/api/login', type='json', auth='public', cors='*')
    def do_login(self, user, password):
        uid = request.session.authenticate(
            request.env.cr.dbname,
            user,
            password
        )
        if not uid:
            return self.errcode(code=400, message='incorrect login')

        token = generate_token(uid)

        user = request.env['res.users'].browse(uid)[0]

        return {'user_id': user[0].id, 'user': user[0].name,
                'partner_id': user[0].partner_id.id, 'email': user[0].email, 'rut': user[0].vat,
                'mobile': user[0].mobile, 'token': token, 'address': user[0].street}

    @http.route('/api/login_truck', type="json", method=['GET'], auth='public', cors='*')
    def do_login_truck(self, user, password):
        uid = request.session.authenticate(
            request.env.cr.dbname,
            user,
            password
        )
        if not uid:
            return self.errcode(code=400, message='incorrect login')

        token = generate_token(uid)

        user = request.env['res.users'].browse(uid)[0]

        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)])

        session = request.env['truck.session'].sudo().search([('user_id', '=', user.id), ('is_login', '=', True)])

        if session:
            return {'user_id': user[0].id, 'user': user[0].name, 'employee_id': employee_id.id,
                    'partner_id': user[0].partner_id.id, 'email': user[0].email, 'rut': user[0].vat,
                    'truck': session.truck_id.name,
                    'mobile': str(user[0].mobile), 'token': token, 'address': user[0].street, 'session': session.id,
                    'is_present': True}
        else:
            return {'user_id': user[0].id, 'user': user[0].name, 'employee_id': employee_id.id,
                    'partner_id': user[0].partner_id.id, 'email': user[0].email, 'rut': user[0].vat,
                    'mobile': user[0].mobile, 'token': token, 'address': user[0].street, 'is_present': True}

    @http.route('/api/assign_truck', type="json", method=['GET'], auth='token', cors='*')
    def assign_truck(self, truck, employee, user):
        truck = truck.strip()
        truck_location = request.env['stock.location'].sudo().search([('name', '=', truck)])
        session = request.env['truck.session'].sudo().search([('truck_id.id', '=', truck_location.id)])
        logging.getLogger().error(session.mapped('is_login'))
        if True in session.mapped('is_login'):
            return "Ya existe una sesion activa con el camion {}".format(truck)
        if truck_location:
            if not employee:
                employee_id = request.env['hr.employee'].search([('user_id', '=', user)])
                session = request.env['truck.session'].sudo().create({
                    'user_id': user,
                    'truck_id': truck_location.id,
                    'employee_id': employee_id.id,
                    'is_login': True,
                })
            else:
                session = request.env['truck.session'].sudo().create({
                    'user_id': user,
                    'truck_id': truck_location.id,
                    'employee_id': employee,
                    'is_login': True,
                })
            return {'ok': True, 'session_id': session.id}
        else:
            return {'ok': False, 'message': "El camion {} no existe".format(truck)}

    @http.route('/api/logout', type='json', auth='public', cors='*')
    def logout(self, session_id):
        session = request.env['truck.session'].sudo().search([('id', '=', session_id)])
        session.sudo().write({
            'is_login': False
        })
        return {'Sesion cerrada exisitosamente'}

    @http.route('/api/refresh-token', type='json', auth='public', cors='*')
    def do_refresh_token(self, email):
        userId = request.env['res.users'].sudo().search_read([('email', '=', email)], ['id'])
        if not userId:
            return self.errcode(code=400, message='incorrect login')
        token = generate_token(userId)

        return {'token': token}

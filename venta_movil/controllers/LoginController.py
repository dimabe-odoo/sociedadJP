from odoo import http
from odoo.http import request
from ..jwt_token import generate_token
import datetime

class LoginController(http.Controller):
    @http.route('/api/login', type='json', auth='public', cors='*')
    def do_login(self, user, password,is_driver= False,truck = ''):
        if not is_driver and truck == '':
            uid = request.session.authenticate(
                request.env.cr.dbname,
                user,
                password
            )
            if not uid:
                return self.errcode(code=400, message='incorrect login')

            token = generate_token(uid)

            user = request.env['res.users'].browse(uid)[0]

            if len(request.env['sale.order'].search([('partner_id', '=', user[0].partner_id.id)])) > 1:
                last_order = request.env['sale.order'].search([('partner_id', '=', user[0].partner_id.id)])[-1]
            else:
                last_order = 'No tiene pedido asociados'

            return {'user': user[0].name, 'last_order': last_order,
                    'partner_id': user[0].partner_id.id, 'email': user[0].email, 'rut': user[0].vat,
                    'mobile': user[0].mobile, 'token': token, 'address': user[0].street}
        else:
            uid = request.session.authenticate(
                request.env.cr.dbname,
                user,
                password
            )
            if not uid:
                return self.errcode(code=400, message='incorrect login')

            token = generate_token(uid)

            user = request.env['res.users'].browse(uid)[0]

            employee_id = request.env['hr.employee'].sudo().search([('user_id','=',user.id)])

            session = request.env['truck.session'].sudo().create({
                'login_datetime':datetime.datetime.now(),
                'user_id':user.id,
                'is_login':True,
                'employee_id':employee_id.id,
                'truck':truck
            })

            return {'user': user[0].name, 'last_order': last_order,'employee_id':employee_id.id,'session_id':session.id,
                    'partner_id': user[0].partner_id.id, 'email': user[0].email, 'rut': user[0].vat,
                    'mobile': user[0].mobile, 'token': token, 'address': user[0].street}

    @http.route('/api/refresh-token', type='json', auth='public', cors='*')
    def do_refresh_token(self, email):
        userId = request.env['res.users'].sudo().search_read([('email', '=', email)], ['id'])
        if not userId:
            return self.errcode(code=400, message='incorrect login')
        token = generate_token(userId)

        return {'token': token}

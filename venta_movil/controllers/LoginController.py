from odoo import http
from odoo.http import request
from ..jwt_token import generate_token
import datetime

class LoginController(http.Controller):
    @http.route('/api/login', type='json', auth='public', cors='*')
    def do_login(self, user, password,is_driver= False):
        if not is_driver:
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

            return {'user': user[0].name,'employee_id':employee_id.id,
                    'partner_id': user[0].partner_id.id, 'email': user[0].email, 'rut': user[0].vat,
                    'mobile': user[0].mobile, 'token': token, 'address': user[0].street}

    @http.route('/api/assign_truck',type="json",method=['GET'],auth='token',cors='*')
    def assign_truck(self,truck,user,employee):
        truck = request.env['stock.location'].search([('name','=',truck)])
        session = request.env['truck.session'].create({
            'user_id':user,
            'truck_i':truck.id,
            'employee_id':employee,
            'is_login':True,
        })
        return {'session_id':session.id}

    @http.route('/api/refresh-token', type='json', auth='public', cors='*')
    def do_refresh_token(self, email):
        userId = request.env['res.users'].sudo().search_read([('email', '=', email)], ['id'])
        if not userId:
            return self.errcode(code=400, message='incorrect login')
        token = generate_token(userId)

        return {'token': token}

from odoo import http
from odoo.http import request
from ..jwt_token import generate_token

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

        return {'user': user[0].name,'points': user[0].partner_id.loyalty_points,'partner_id' : user[0].partner_id.id, 'email': user[0].email, 'rut': user[0].vat, 'mobile': user[0].mobile, 'token': token, 'address': user[0].street}


    @http.route('/api/refresh-token', type='json', auth='public', cors='*')
    def do_refresh_token(self, email):
        userId = request.env['res.users'].sudo().search_read([('email', '=', email)], ['id'])
        if not userId:
            return self.errcode(code=400, message='incorrect login')
        token = generate_token(userId)

        return {'token': token}


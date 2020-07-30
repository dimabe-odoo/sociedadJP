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

        return {'user': user[0].name, 'token': token, 'address': user[0].street}


    @http.route('/api/login', type='json', auth='public', cors='*')
    def do_refresh_token(self, email):
        user = request.env['res.users'].sudo().search_read([('id', '=', request.uid)], ['id'])
        if not user:
            return self.errcode(code=400, message='incorrect login')
        token = generate_token(user.id)

        return {'token': token}


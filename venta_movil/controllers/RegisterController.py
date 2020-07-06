from odoo import http
from odoo.http import request
from ..jwt_token import generate_token

class LoginController(http.Controller):
    @http.route('/api/register', type='json', auth='public', cors='*')
    def do_register(self, name, password, email, phoneNumber):
        # search user exist
        user = request.env['res.users'].sudo().search([('email', '=', email)])

        if user:
            return self.errcode(code=400, message='Usuario registrado con anterioridad')

        contact = request.env['res.partner'].sudo().search([('email', '=', email)])

        if contact: 
            contact.write({'name': name, 'email': email, 'mobile': phoneNumber})
        else:
            request.env['res.partner'].sudo().create({'name': name, 'email': email, 'mobile': phoneNumber})
        
        request.env['res.users'].sudo().create({'name': name, 'login': email, 'password': password})

        uid = request.session.authenticate(
            request.env.cr.dbname,
            email,
            password
        )

        if not uid:
            return self.errcode(code=400, message='No se pudo conectar al sistema')

        token = generate_token(uid)

        return {'user': uid, 'token': token}
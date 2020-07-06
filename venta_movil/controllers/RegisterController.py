from odoo import http
from odoo.http import request
from ..jwt_token import generate_token
import werkzeug

class RegisterController(http.Controller):
    @http.route('/api/register', type='json', auth='public', cors='*')
    def do_register(self, name, password, email, phoneNumber):
        # search user exist
        user = request.env['res.users'].sudo().search([('login', '=', email)])

        if user:
            raise werkzeug.exceptions.BadRequest('el email {} ya se encuentra registrado'.format(email))

        contact = request.env['res.partner'].sudo().search([('email', '=', email)])

        if contact: 
            contact.write({'name': name, 'email': email, 'mobile': phoneNumber})
        else:
            request.env['res.partner'].sudo().create({'name': name, 'email': email, 'mobile': phoneNumber})
        
        create_user = request.env['res.users'].sudo().create({
        'name': name, 
        'login': email,
        'password': password, 
        'company_id':1,
        'sel_groups_1_8_9':8})



        return {'message': 'Usuario creado correctamente', 'user': create_user}
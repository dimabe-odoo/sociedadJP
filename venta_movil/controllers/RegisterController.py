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

        partner = request.env['res.partner'].sudo().search([('email', '=', email)])

        if partner: 
            partner.write({'name': name, 'email': email, 'mobile': phoneNumber})
        else:
            partner = request.env['res.partner'].sudo().create({'name': name, 'email': email, 'mobile': phoneNumber})
        
        create_user = request.env['res.users'].sudo().create({
        'name': name, 
        'login': email,
        'email': email,
        'password': password, 
        'company_id':1,
        'sel_groups_1_8_9':8,
        'partner_id': partner[0].id,
        'mobile': phoneNumber})

        token = generate_token(create_user[0].id)


        return {'message': 'Usuario creado correctamente', 'user': create_user[0].name, 'token': token}
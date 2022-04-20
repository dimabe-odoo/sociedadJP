from odoo import http
from odoo.http import request
from ..jwt_token import generate_token
import werkzeug


class RegisterController(http.Controller):
    @http.route('/api/register', type='json', auth='public', cors='*')
    def do_register(self, name, password, email, phoneNumber, commune, street):
        # search user exist
        email = email.lower()
        user = request.env['res.users'].sudo().search([('login', '=', email)])
        if user:
            raise werkzeug.exceptions.BadRequest(
                'el email {} ya se encuentra registrado'.format(email))

        partner = request.env['res.partner'].sudo().search(
            [('email', '=', email)])

        if partner:
            partner.write(
                {'name': name, 'email': email, 'mobile': phoneNumber})
        else:
            partner = request.env['res.partner'].sudo().create(
                {'name': name, 'email': email, 'mobile': phoneNumber})

        create_user = request.env['res.users'].sudo().create({
            'name': name,
            'login': email,
            'email': email,
            'password': password,
            'street': street,
            'company_id': 1,
            'property_product_pricelist': 3,
            'sel_groups_1_8_9': 8,
            'partner_id': partner[0].id,
            'mobile': phoneNumber})

        token = generate_token(create_user[0].id)

        return {'message': 'Usuario creado correctamente', 'user': create_user[0].name, 'email': create_user[0].email,
                'mobile': create_user[0].mobile, 'address': create_user[0].street, 'token': token}

    @http.route('/api/create_client', type='json', method=['POST'], auth='token', cors='*')
    def create_client(self, name, email, phoneNumber, commune_id, address, latitude, longitude, reference, vat=False):
        try:
            email = email.lower()
            user = request.env['res.users'].sudo().search([('login', '=', email)])

            if user:
                return {'message': 'el email {} ya se encuentra registrado'.format(email)}
            partner = request.env['res.partner'].sudo().search(
                [('vat', '=', vat)])
            if partner:
                return {'message': 'el rut ingresado ya esta registrado'}

            partner = request.env['res.partner'].sudo().search(
                [('email', '=', email)])

            commune = request.env['jp.commune'].search([('id', '=', commune_id)])

            if partner:
                partner.write({'name': name, 'email': email, 'mobile': phoneNumber,
                               'street': address, 'partner_latitude': latitude, 'partner_longitude': longitude,
                               'jp_commune_id': commune.id, 'state_id': commune.state_id.id, 'comment': reference})
            else:
                partner = request.env['res.partner'].sudo().create(
                    {'name': name, 'email': email, 'mobile': phoneNumber, 'jp_commune_id': commune.id,
                     'state_id': commune.state_id.id, 'property_product_pricelist': 5, 'street': address,
                     'partner_latitude': latitude,
                     'partner_longitude': longitude, 'l10n_cl_sii_taxpayer_type': '1', 'vat': vat,
                     'comment': reference})

            user = request.env['res.users'].sudo().search([('login', '=', email)])
            if not user:
                create_user = request.env['res.users'].sudo().create({
                    'name': name,
                    'login': email,
                    'email': email,
                    'company_id': 1,
                    'sel_groups_1_8_9': 8,
                    'partner_id': partner.id,
                    'mobile': phoneNumber,
                    'comment': reference
                })

            return {'message': "Cliente creado correctamente", 'clientId': partner.id}
        except Exception as e:
            return {'message': "Error al crear el cliente"}

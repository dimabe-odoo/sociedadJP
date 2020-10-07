from odoo import http
from odoo.http import request
from datetime import date
import werkzeug


class AddressController(http.Controller):

    @http.route('/api/addresses', type='json', methods=['POST'], auth='token', cors='*')
    def get_communes(self, commune_id, city, address, latitude, longitude):
        partner_id = request.env['res.users'].sudo().search([('id', '=', request.uid)])[0].partner_id
        if not partner_id:
            raise werkzeug.exceptions.BadRequest('Imposible encontrar el contacto asociado al usuario')

        partner_id.write({'state_id': 1176, 'jp_commune_id': int(commune_id), 'city': city, 'street': address,
                          'partner_latitude': float(latitude), 'partner_longitude': float(longitude),
                          'date_localization': date.today()})

        return {'message': 'Dirección creada correctamente'}

    @http.route('/api/add_address', type='json', methods=['POST'], auth='token', cors='*')
    def add_address(self, city, address, name, partner_id,commune_id, email, phone, reference):
        partner = request.env['res.partner'].search([('id', '=', partner_id)])
        res = request.env['res.partner'].sudo().create({
            'type': 'other',
            'name': name,
            'street': address,
            'city': city,
            'jp_commune_id' : commune_id,
            'email': email,
            'mobile': phone,
            'parent_id': partner_id,
            'comment': reference
        })
        return res

    @http.route('/api/get_address', type='json', methods=['POST'], auth='token', cors='*')
    def get_address(self, partner_id):
        childs = request.env['res.partner'].search([('id', '=', partner_id)]).child_ids
        res = []
        for child in childs:
            res.append({
                'name': child.name,
                'street': child.street,
                'city': child.city,
                'mobile': child.phone,
                'references': child.comment,
            })
        return res

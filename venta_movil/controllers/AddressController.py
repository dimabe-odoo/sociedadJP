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
    def add_address(self, address, name, partner_id, commune_id, email, phone, latitude, longitude, reference=False):
        partner = request.env['res.partner'].search([('id', '=', partner_id)])
        res = request.env['res.partner'].sudo().create({
            'type': 'other',
            'name': name,
            'street': address,
            'partner_latitude': float(latitude),
            'partner_longitude': float(longitude),
            'jp_commune_id': commune_id,
            'email': email,
            'mobile': phone,
            'parent_id': partner_id,
            'comment': reference
        })
        return {'message': 'Direccion creada correctamente'}

    @http.route('/api/edit_address', type='json', methods=['POST'], auth='token', cors='*')
    def edit_address(self, partner_id, name, phone, email, address, latitude, longitude):
        partner_id = request.env['res.partner'].sudo().search([('id', '=', partner_id)]).write({
            'name': name,
            'mobile': phone,
            'email': email,
            'street': address,
            'partner_latitude': float(latitude),
            'partner_longitude': float(longitude),
        })
        return {"Direccion Modificada"}

    @http.route('/api/get_address', type='json', methods=['POST'], auth='token', cors='*')
    def get_address(self, partner_id):
        childs = request.env['res.partner'].search([('id', '=', partner_id)]).child_ids
        res = []
        if childs:
            for child in childs:
                if request.env['res.partner'].search([('address_favorite_id', '=', child.id)]):
                    is_favorite = True
                else:
                    is_favorite = False
                res.append({
                    'id': child.id,
                    'name': child.name,
                    'street': child.street,
                    'city': child.city,
                    'mobile': child.mobile,
                    'commune': child.jp_commune_id.name,
                    'references': child.comment if child.comment else '',
                    'is_favorite': is_favorite
                })
        else:
            partner = request.env['res.partner'].search([('id', '=', partner_id)])
            res.append({
                'id': partner.id,
                'name': partner.name,
                'street': partner.street if partner.street else '',
                'city': partner.city if partner.city else '',
                'mobile': partner.mobile if partner.mobile else '',
                'commune': partner.jp_commune_id.name,
                'references': partner.comment if partner.comment else '',
                'is_favorite': True
            })
        return res

    @http.route('/api/delete_address', type='json', method=['POST'], auth='token', cors='*')
    def delete(self, partner_id):
        partner_id = request.env['res.partner'].search([('id', '=', partner_id)])
        if not partner_id.parent_id:
            return {'message': "No puede eliminar la direccion principal de su usuario"}
        partner_id.sudo().write({
            'parent_id': None
        })

        return {'message': 'Direccion eliminada correctamente'}

    @http.route('/api/set_favorite', type='json', method=['POST'], auth='token', cors='*')
    def set_favorite(self, partner_id, address_id):
        partner_id = request.env['res.partner'].search([('id', '=', partner_id)])
        partner_id.sudo().write({
            'address_favorite_id': None
        })
        partner_id.sudo().write({
            'address_favorite_id': address_id
        })
        return {'message': f"Se ha definido como favorita a {partner_id.address_favorite_id.name}"}

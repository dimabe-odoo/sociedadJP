from odoo import http
from odoo.http import request
from datetime import date
import werkzeug

class AddressController(http.Controller):

    @http.route('/api/addresses', type='json', methods=['POST'], auth='token', cors='*')
    def get_communes(self, commune_id, city, address, latitude, longitude):
        partner_id = request.env['res.users'].sudo().search_read([('id', '=', request.uid)], ['partner_id'])
        raise werkzeug.exceptions.BadRequest(partner_id)
        contact = request.env['res.partner'].sudo().browse(partner_id)
        if not contact:
            raise werkzeug.exceptions.BadRequest('Imposible encontrar el contacto asociado al usuario {}'.format(contact))

        contact.update({'state_id': 1176,'jp_commune_id': int(commune_id), 'city': city, 'street': address, 'partnet_latitude': float(latitude), 'partner_longitude': float(longitude)})

        return {'message': 'Dirección creada correctamente'}
        
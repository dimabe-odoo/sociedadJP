from odoo import http
from odoo.http import request
from datetime import date
import werkzeug

class AddressController(http.Controller):

    @http.route('/api/addresses', type='json', methods=['POST'], auth='token', cors='*')
    def get_communes(self, commune_id, city, address, latitude, longitude):
        contact = request.env['res.partner'].sudo().search(['user_id', '=', request.uid])
        if not contact:
            raise werkzeug.exceptions.BadRequest('Imposible encontrar el contacto asociado al usuario')
        contact.write({'state_id': 1176,'jp_commune_id': commune_id, 'city': city, 'street': address, 'partnet_latitude': latitude, 'partner_longitude': longitude, 'date_localization': date.today()})

        return {'message': 'Dirección creada correctamente'}
        
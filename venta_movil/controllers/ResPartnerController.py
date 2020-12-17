from odoo import http
from odoo.http import request
import datetime
import logging
import googlemaps


class ResPartnerController(http.Controller):

    @http.route('/api/clients', type='json', method=['GET'], auth='token', cors='*')
    def get_clients(self):
        respond = request.env['res.partner'].search([])
        result = []
        now = datetime.datetime.now()
        _logger = logging.getLogger(__name__)
        for res in respond:
            another = []
            for c in res.child_ids:
                another.append({
                    'Id': str(res.id),
                    'Name': c.name,
                    'Address': c.street,
                    'Latitude': c.partner_latitude,
                    'Longitude': c.partner_longitude,
                    'Phone': c.mobile,
                    })
            result.append({
                'Id': str(res.id),
                'Name': res.name,
                'Address': res.street,
                'Latitude': res.partner_latitude,
                'Longitude': res.partner_longitude,
                'Phone': res.mobile,
                'AnotherDirection': another
                })
        return result

from odoo import http
from odoo.http import request
import datetime
import logging
import googlemaps


class ResPartnerController(http.Controller):

    @http.route('/api/clients', type='json', method=['GET'], auth='token', cors='*')
    def get_clients(self, latitude, longitude):
        respond = request.env['res.partner'].search([])
        result = []
        now = datetime.datetime.now()
        gmaps = googlemaps.Client(key='AIzaSyByqie1H_p7UUW2u6zTIynXgmvJUdIZWx0')
        for res in respond:
            dir = gmaps.directions((latitude, longitude),
                                   (res.partner_latitude, res.partner_longitude),
                                   mode="driving", departure_time=now)
            another = []
            for c in res.child_ids:
                dir_another = gmaps.directions((latitude, longitude),
                                               (c.partner_latitude, c.partner_longitude),
                                               mode="driving", departure_time=now)
                another.append({
                    'Id': str(res.id),
                    'Name': res.name,
                    'Address': res.street,
                    'Latitude': res.partner_latitude,
                    'Longitude': res.partner_longitude,
                    'Phone': res.mobile,
                    'Distance': dir_another[0]['legs'][0]['distance']['text']
                })
            result.append({
                'Id': str(res.id),
                'Name': res.name,
                'Address': res.street,
                'Latitude': res.partner_latitude,
                'Longitude': res.partner_longitude,
                'Phone': res.mobile,
                'AnotherDirection': another,
                'Distance': dir[0]['legs'][0]['distance']['text']
            })
        return result

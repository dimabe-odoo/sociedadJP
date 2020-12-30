from odoo import http
from odoo.http import request
import datetime
import logging
import googlemaps


class ResPartnerController(http.Controller):


    @http.route('/api/clients', type='json', method=['GET'], auth='token', cors='*')
    def get_clients(self, truck):
        respond = request.env['res.partner'].sudo().search([])
        location = request.env['stock.location'].sudo().search([('name', '=', truck)])
        stock = request.env['stock.quant'].sudo().search([('location_id', '=', location.id)])

        result = []
        now = datetime.datetime.now()
        _logger = logging.getLogger(__name__)
        _logger.error(stock.mapped('product_id'))
        for res in respond:
            result.append({
                'Id': str(res.id),
                'Name': res.name,
                'Address': res.street,
                'Latitude': res.partner_latitude,
                'Longitude': res.partner_longitude,
                'Phone': res.mobile,
            })
        return result

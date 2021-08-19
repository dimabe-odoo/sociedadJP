from odoo import http
from odoo.http import request
import json
import datetime
import logging
from odoo.tools import date_utils
import googlemaps
from ..utils import get_price_product

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
                'Id': res.id,
                'Name': res.name,
                'Address': res.street,
                'Latitude': res.partner_latitude,
                'Longitude': res.partner_longitude,
                'Phone': res.mobile,
            })
        return result

    @http.route('/api/client', type='json', method=['GET'], auth='token', cors='*')
    def get_client(self, client,truck):
        client_object = request.env['res.partner'].sudo().search([('id', '=', client)])
        _logger = logging.getLogger(__name__)
        _logger.error(f'{client} {client_object}')
        raw_data = client_object.read()
        _logger.error(f'{client} {raw_data}')
        json_data = json.dumps(raw_data, default=date_utils.json_default)
        json_dict = json.loads(json_data)
        price = get_price_product.get_prices(client_id=client,truck=truck)
        json_dict[0]['price_list'] = price
        return json_dict[0]


    @http.route('/api/images', type='json', method=['GET'], auth='public', cors='*')
    def get_image(self):
        list_products = request.env['product.product'].sudo().search([])
        result = []
        for product in list_products:
            if "Cilindro" in product.name:
                result.append({
                    "name": product.display_name,
                    "image1902": product.image_1920
                })
        return result

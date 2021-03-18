from odoo import http
from odoo.http import request
import json
import datetime
import logging
from odoo.tools import date_utils
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
                'Id': res.id,
                'Name': res.name,
                'Address': res.street,
                'Latitude': res.partner_latitude,
                'Longitude': res.partner_longitude,
                'Phone': res.mobile,
            })
        return result

    @http.route('/api/client', type='json', method=['GET'], auth='token', cors='*')
    def get_client(self, client):
        client_object = request.env['res.partner'].sudo().search([('id', '=', client)])
        _logger = logging.getLogger(__name__)
        _logger.error(f'{client} {client_object}')
        raw_data = client_object.read()
        _logger.error(f'{client} {raw_data}')
        json_data = json.dumps(raw_data, default=date_utils.json_default)
        json_dict = json.loads(json_data)
        return json_dict[0]

    @http.route('/api/prices', type='json', method='GET', auth='token', cors='*')
    def get_prices(self, client_id, truck):
        client = request.env['res.partner'].sudo().search([('id', '=', client_id)])
        result = []
        location = request.env['stock.location'].sudo().search([('name', '=', truck)])
        stock = request.env['stock.quant'].sudo().search([('location_id', '=', location.id)])
        for pr in client.sudo().property_product_pricelist.item_ids:
            product = request.env['product.product'].sudo().search(
                [('product_tmpl_id', '=', pr.product_tmpl_id.id)])
            stock_product = stock.filtered(lambda a: a.product_id.id == product.id)
            taxes_amount = (int(sum(product.mapped('taxes_id').mapped('amount'))) / 100) + 1

            result.append({
                'Product_Id': pr.product_tmpl_id.id,
                'Product_Name': pr.product_tmpl_id.name,
                'isCat': True if 'Catalítico' in pr.product_tmpl_id.display_name else False,
                'is_Dist': True if 'Descuento' in pr.product_tmpl_id.display_name or 'Discount' in pr.product_tmpl_id.display_name else False,
                'Stock': stock_product.quantity,
                'Price': pr.fixed_price
            })
        for coupon in request.env['product.product'].sudo().search([('categ_id', '=', 7)]):
            result.append({
                'Product_Id': coupon.product_tmpl_id.id,
                'Product_Name': coupon.product_tmpl_id.name,
                'isCat': True if 'Catalítico' in coupon.product_tmpl_id.display_name else False,
                'is_Dist': True if 'Descuento' in coupon.product_tmpl_id.display_name or 'Discount' in coupon.product_tmpl_id.display_name else False,
                'Stock': 1,
                'Price': coupon.list_price
            })
        for cil in request.env['product.product'].sudo().search([('categ_id', '=', 7)]):
            result.append({
                'Product_Id': cil.product_tmpl_id.id,
                'Product_Name': cil.product_tmpl_id.name,
                'isCil': True,
            })
        return result

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

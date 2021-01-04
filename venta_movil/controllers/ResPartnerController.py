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

    @http.route('/api/client',type='json',method=['GET'],auth='token',cors='*')
    def get_client(self,client):
        client = request.env['res.partner'].sudo().search([('id','=',client)])
        raw_data = client.read()
        json_data = json.dumps(raw_data,default=date_utils.json_default)
        return raw_data

    @http.route('/api/prices',type='json',method='GET',auth='token',cors='*')
    def get_prices(self,client_id,truck):
        client = request.env['res.partner'].sudo().search([('id','=',client_id)])
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
                'Price': pr.fixed_price * taxes_amount
            })

        return result
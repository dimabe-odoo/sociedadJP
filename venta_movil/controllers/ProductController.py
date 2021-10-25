from odoo import http
from odoo.http import request
import json
from odoo.tools import date_utils


class ProductController(http.Controller):

    @http.route('/api/get_products', type='json', method='GET', auth='token', cors='*')
    def get_products(self, client):
        partner = request.env['res.partner'].sudo().search([('id', '=', client)])
        result = []
        if partner.property_product_pricelist.item_ids:
            pricelist_id = partner.property_product_pricelist.item_ids
            products = request.env['product.product'].sudo().search([])
            for product in products:
                raw_data = product.read()
                json_data = json.dumps(raw_data, default=date_utils.json_default)
                json_dict = json.loads(json_data)
                if pricelist_id.filtered(lambda x: x.product_tmpl_id.id == product.product_tmpl_id.id):
                    json_dict[0]['price'] = pricelist_id.filtered(
                        lambda x: x.product_tmpl_id.id == product.product_tmpl_id.id).fixed_price
                else:
                    json_dict[0]['price'] = product.list_price
                result.append(json_dict)
        return result

    @http.route('/api/get_product_truck', type='json', method='GET', auth='token', cors='*')
    def get_product_truck(self):
        result = request.env['product.product'].sudo().search([])
        data = []
        for res in result:
            data.append({
                'Id': res.id,
                'ProductName': res.display_name,
                'isCat': True if 'Catalítico' in res.display_name else False,
                'ImageBase64': res.image_1920
            })
        return data

    @http.route('/api/get_stock_truck', type='json', method='GET', auth='token', cors='*')
    def get_stock_product_truck(self, truck):
        truck_stock = request.env['stock.quant'].search([('location_id.name', '=', truck)])
        trucks = []
        for truck in truck_stock:
            trucks.append({
                'ProductName': truck.product_id.name,
                'Quantity': int(truck.quantity)
            })
        print(trucks)
        return trucks

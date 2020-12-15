from odoo import http
from odoo.http import request


class ProductController(http.Controller):

    @http.route('/api/get_products', type='json', method='GET', auth='token', cors='*')
    def get_products(self):
        result = request.env['res.users'].sudo().search([('id', '=', request.uid)])[
            0].partner_id.property_product_pricelist.item_ids
        data = []
        for res in result:
            data.append({
                'id': res.product_tmpl_id.id,
                'name': res.product_tmpl_id.name,
                'price': res.fixed_price,
            })

        return data

    @http.route('/api/get_product_truck', type='json', method='GET', auth='token', cors='*')
    def get_product_truck(self):
        result = request.env['product.product'].sudo().search([])
        data = []
        for res in result:
            data.append({
                'Id': res.id,
                'ProductName': res.display_name,
                'isCat': True if 'Catalitico' in res.display_name else False
            })

from odoo import http
from odoo.http import request


class ProductController(http.Controller):

    @http.route('/api/get_products', type='json', method='GET', auth='token', cors='*')
    def get_products(self):
        result = request.env['product.product'].sudo().search([])
        data = []
        for res in result:
            data.append({
                'id': res.product_tmpl_id.id,
                'name': res.product_tmpl_id.name,
                'image_1920':res.image_1920
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
                'isCat': True if 'Catalítico' in res.display_name else False
            })
        return data

from odoo import http
from odoo.http import request

class ProductController(http.Controller):

    @http.route('/api/products',type='json',method='GET',auth='token',cors='*')
    def get_products(self):
        result = request.env['product.product'].search([])
        data = []
        for res in result:
            data.append({
                'id': res.id,
                'name': res.name,
                #'price': res.fixed_price,
                'photo':res.image_1024
            })

        return data
from odoo import http
from odoo.http import request


class ProductController(http.Controller):

    @http.route('/api/products', type='json', method='GET', auth='token', cors='*')
    def get_products(self):
        result = request.env['product.product'].search([])
        data = []
        for res in result:
            price = request.env['product.pricelist'].search(
                [('name', '=', 'Tarifa Publica Reparto')]).item_ids.filtered(
                lambda a: a.product_tmpl_id.id == res.product_tmpl_id.id).fixed_price
            data.append({
                'id': res.id,
                'name': res.name,
                'price': price,
                'photo': res.image_1024
            })

        return data

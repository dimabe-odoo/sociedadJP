from odoo import http
from odoo.http import request


class ProductController(http.Controller):

    @http.route('/api/get_products', type='json', method='GET', auth='token', cors='*')
    def get_products(self):
        result = request.env['product.product'].search([])
        data = []
        for res in result:
            price = request.env['product.pricelist'].search(
                [('name', '=', 'Tarifa Publica Reparto')]).item_ids.filtered(
                lambda a: a.product_tmpl_id.id == res.product_tmpl_id.id).fixed_price
            if price == 0:
                continue
            data.append({
                'id': res.id,
                'name': res.name,
                'price': price,
            })

        return data

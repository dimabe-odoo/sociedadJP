from odoo import http
from odoo.http import request


class ProductController(http.Controller):

    @http.route('/api/get_products', type='json', method='GET', auth='token', cors='*')
    def get_products(self):
        result = request.env['res.users'].sudo().search([('id', '=', request.uid)])[0].partner_id.property_product_pricelist.item_ids
        data = []
        for res in result:
            data.append({
                'id': res.product_tmpl_id.id,
                'name': res.product_tmpl_id.name,
                'price': res.fixed_price,
            })

        return data

from odoo import http
from odoo.http import request

class ProductController(http.Controller):

    @http.route('/api/products',type='json',method='GET',auth='token',cors='*')
    def get_products(self):
        result = request.env['product.pricelist'].search([('name','=','Tarifa Publica Reparto')]).item_ids
        data = []
        for res in result:
            data.append({
                'id':res.product_tmpl_id.id,
                'name':res.product_tmpl_id.name,
                'price': res.fixed_price,
            })

        return data
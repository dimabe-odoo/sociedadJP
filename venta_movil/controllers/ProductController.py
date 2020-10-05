from odoo import http
from odoo.http import request

class ProductController(http.Controller):

    @http.route('/api/products',type='json',method='GET',auth='token',cors='*')
    def get_products(self):
        result = request.env['product.pricelist'].search([('name','=','Tarifa Publica Reparto')]).item_ids
        data = []
        for res in result:
            product = request.env['product.product'].search([('product_tmpl_id','=',res.product_tmpl_id.id)])
            data.append({
                'id': product.id,
                'name': product.name,
                'price': res.fixed_price,
            })

        return data
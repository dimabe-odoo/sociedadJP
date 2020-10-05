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
                'image_1024' : res.product_tmpl_id.image_1024,
                'image_128' : res.product_tmpl_id.image_128,
                'image_1920' : res.product_tmpl_id.image_1920,
                'image_256' : res.product_tmpl_id.image_256
            })

        return data
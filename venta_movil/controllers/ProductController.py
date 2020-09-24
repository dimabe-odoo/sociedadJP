from odoo import http
from odoo.http import request

class ProductController(http.Controller):

    @http.route('/api/products',type='json',method='GET',auth='token',cors='*')
    def get_products(self):
        result = request.env['product.product'].search([('categ_id.name','=','Venta Gas')])
        data = []
        for res in result:
            data.append({
                'id':res.id,
                'name':res.display_name,
            })

        return data
from odoo import http
from odoo.http import request

class ProductController(http.Controller):

    @http.route('/api/products',type='json',method='GET',auth='token',cors='*')
    def get_products(self):
        result = request.env['product.product'].search([('categ_id.name','=','Venta Gas')])
        data = []
        for res in result:
            data.append({
                'ProductName':res.name,
                'Price':res.list_price
            })
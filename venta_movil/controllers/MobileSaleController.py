from odoo import http
from odoo.http import request
import datetime

class MobileSaleController(http.Controller):

    @http.route('/api/create_sale',type='json',method=['POST'],auth='public',cors='*')
    def create_sale(self,customer_id,saleman_id,product_id):
        customer_id = request.env['res.partner'].sudo().search([('id','=',customer_id)])
        saleman_id = request.env['res.partner'].sudo().search([('id','=',saleman_id)])
        product_id = request.env['product.product'].sudo().search([('id','=',product_id)])

        name = request.env['ir.sequence'].sudo().next_by_code('mobile.sale.order')

        sale_order = request.env['mobile.sale.order'].create({
            'name':name,
            'customer_id':customer_id.id,
            'saleman_id':saleman_id.id,
            'product_id':product_id.id,
            'state':'progress'
        })

        return {'sale_order':sale_order.name}
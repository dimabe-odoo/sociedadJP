from odoo import http
from odoo.http import request
import datetime

class MobileSaleController(http.Controller):

    @http.route('/api/sale/create_sale',type='json',method=['POST'],auth='public',cors='*')
    def create_sale(self,customer_id,saleman_id,product_ids,location_id):
        customer = request.env['res.partner'].sudo().search([('id','=',customer_id)])
        saleman = request.env['res.partner'].sudo().search([('id','=',saleman_id)])
        products = request.env['product.product'].sudo().search([('id','in',product_ids)])
        location = request.env['stock.location'].sudo().search([('id','=',location_id)])

        name = request.env['ir.sequence'].sudo().next_by_code('mobile.sale.order')

        total = sum(products.mapped('list_price'))

        sale_order = request.env['mobile.sale.order'].sudo().create({
            'name':name,
            'customer_id':customer.id,
            'saleman_id':saleman.id,
            'product_ids':products,
            'total':total,
            'location_id':location.id,
            'state':'progress'
        })

        return {'message':'Compra realizada satifactoriamente','sale_order':sale_order.id,'total':sale_order.total}

    @http.route('/api/sale/make_done',type='json',method=['GET'],auth='public',cors='*')
    def make_done(self,mobile_id):
        mobile_order = request.env['mobile.sale.order'].sudo().search([('id','=',mobile_id)])

        mobile_order.write({'state':'done','date_done':datetime.datetime.now})

        return {'mobile_order',mobile_order.name}
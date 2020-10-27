from odoo import http
from odoo.http import request
import datetime
import logging


class MobileSaleController(http.Controller):

    @http.route('/api/sale/create_sale', type='json', method=['POST'], auth='public', cors='*')
    def create_sale(self, product_ids, is_loan=False):
        customer = request.env['res.partner'].sudo().search([('id', '=', request.uid)])
        name = request.env['ir.sequence'].sudo().next_by_code('mobile.sale.order')

        sale_order = request.env['mobile.sale.order'].sudo().create({
            'name': name,
            'customer_id': customer.id,
            'state': 'progress',
            'is_loan': is_loan
        })

        for product in product_ids:
            logging.error('{}'.format(product))
            line = request.env['mobile.sale.line'].sudo().create({
                'product_id': product['id'],
                'price': product['price'],
                'state': 'progress',
                'qty': product['qty'],
                'mobile_id': sale_order.id
            })

        return {'message': 'Compra realizada satifactoriamente', 'sale_order': sale_order.id}

    @http.route('/api/sale/take_saleman', type="json", method=['GET'], auth='public', cors='*')
    def take_saleman(self, mobile_id, location_saleman):
        mobile_order = request.env['mobile.sale.order'].search([('id', '=', mobile_id)])
        mobile_order.write('location_id', '=', location_saleman)

    @http.route('/api/sale/make_done', type='json', method=['GET'], auth='public', cors='*')
    def make_done(self, mobile_id):
        mobile_order = request.env['mobile.sale.order'].sudo().search([('id', '=', mobile_id)])

        mobile_order.write({'state': 'done', 'date_done': datetime.datetime.now})

        return {'mobile_order', mobile_order.name}

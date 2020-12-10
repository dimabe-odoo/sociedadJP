from odoo import http
from odoo.http import request
import datetime
import logging
import haversine as hs
from haversine import Unit


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
    def take_saleman(self, mobile_id, session):
        mobile_order = request.env['mobile.sale.order'].search([('id', '=', mobile_id)])
        truck_session = request.env['truck.session'].sudo().search([('id', '=', int(session))])
        _logger = logging.getLogger(__name__)
        _logger.error(truck_session)
        warehouses = request.env['stock.warehouse'].sudo().search([])
        warehouse_id = 0
        for ware in warehouses:
            trucks = ware.mapped('truck_ids').mapped('id')
            if truck_session.truck_id.id in trucks:
                warehouse_id = ware.id
                break
        mobile_order.write({
            'seller_id': session,
            'location_id': truck_session.truck_id.id,
            'warehouse_id': warehouse_id
        })
        mobile_order.button_dispatch()
        return {'Pedido asignado'}

    @http.route('/api/sale/make_done', type='json', method=['GET'], auth='public', cors='*')
    def make_done(self, mobile_id):
        mobile_order = request.env['mobile.sale.order'].sudo().search([('id', '=', mobile_id)])

        mobile_order.write({'state': 'done', 'date_done': datetime.datetime.now})

        return {'mobile_order', mobile_order.name}

    @http.route('/api/mobile_orders', type="json", method=['GET'], auth='token', cors='*')
    def get_orders(self, latitude, longitude):
        env = request.env['mobile.sale.order'].sudo().search([('state', '=', 'confirm')])
        respond = []
        loc_truck = (longitude, latitude)

        for res in env:
            description = ''
            array_srt_des = []
            array_des = []
            s = ' '
            loc_customer = (res.customer_id.partner_longitude, res.customer_id.partner_latitude)
            dis = hs.haversine(loc_truck, loc_customer, Unit.METERS)
            for product in res.mobile_lines:
                if product.qty > 1:
                    array_srt_des.append('{} {}s'.format(product.qty, product.product_id.name))
                    array_des.append({
                        'ProductName': product.product_id.name,
                        'Qty': product.qty,
                        'PriceUnit': product.price
                    })
                else:
                    array_srt_des.append('{} {}'.format(product.qty, product.product_id.name))
                    array_des.append({
                        'ProductName': product.product_id.name,
                        'Qty': product.qty,
                        'PriceUnit': product.price
                    })
            description = s.join(array_srt_des)
            respond.append({
                'id': str(res.id),
                'ClientName': res.customer_id.display_name,
                'ClientAddress': res.customer_id.street,
                'ClientPhone': res.customer_id.mobile,
                'ShortDescription': description,
                'Distance': round(dis, 2),
                'Description': array_des
            })
        list_sort_by_dis = sorted(respond, key=lambda i: i['Distance'])
        return list_sort_by_dis

    @http.route('/api/my_orders', type='json', method=['GET'], auth='token', cors='*')
    def get_my_orders(self, session, latitude, longitude):
        mobile_orders = request.env['mobile.sale.order'].search([('session_id', '=', session)])
        respond = []
        loc_truck = (longitude, latitude)

        for res in mobile_orders:
            description = ''
            array_srt_des = []
            array_des = []
            s = ' '
            loc_customer = (res.customer_id.partner_longitude, res.customer_id.partner_latitude)
            dis = hs.haversine(loc_truck, loc_customer, Unit.METERS)
            for product in res.mobile_lines:
                if product.qty > 1:
                    array_srt_des.append('{} {}s'.format(product.qty, product.product_id.name))
                    array_des.append({
                        'ProductName': product.product_id.name,
                        'Qty': product.qty,
                        'PriceUnit': product.price
                    })
                else:
                    array_srt_des.append('{} {}'.format(product.qty, product.product_id.name))
                    array_des.append({
                        'ProductName': product.product_id.name,
                        'Qty': product.qty,
                        'PriceUnit': product.price
                    })
            description = s.join(array_srt_des)
            respond.append({
                'id': str(res.id),
                'ClientName': res.customer_id.display_name,
                'ClientAddress': res.customer_id.street,
                'ClientPhone': res.customer_id.mobile,
                'ShortDescription': description,
                'Distance': round(dis, 2),
                'Description': array_des
            })
        list_sort_by_dis = sorted(respond, key=lambda i: i['Distance'])
        return list_sort_by_dis

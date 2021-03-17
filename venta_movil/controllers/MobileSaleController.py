from odoo import http
from odoo.http import request
import datetime
import logging
import json
import functools
import googlemaps
import requests
import math


class MobileSaleController(http.Controller):

    @http.route('/api/create_mobile', type='json', method=['POST'], auth='public', cors='*')
    def create_sale(self, customer_id, product_ids, session, payment):
        customer = request.env['res.partner'].sudo().search([('id', '=', customer_id)])
        session = request.env['truck.session'].sudo().search([('id', '=', session)])
        logging.getLogger().error('Payment {}'.format(payment))
        warehouses = request.env['stock.warehouse'].sudo().search([])
        warehouse_id = 0
        for ware in warehouses:
            trucks = ware.mapped('truck_ids').mapped('id')
            if session.truck_id.id in trucks:
                warehouse_id = ware.id
                break
        mobile = request.env['mobile.sale.order'].sudo().create({
            'state': 'draft',
            'customer_id': customer.id,
            'price_list_id': customer.property_product_pricelist.id
        })
        now = datetime.datetime.now()
        logging.error(dir)
        line = []
        for product in product_ids:
            product_json = json.loads(product)
            product_object = request.env['product.product'].sudo().search([('id', '=', int(product_json['id']))])
            logging.getLogger().error(product_object.taxes_id)
            sale_line = request.env['mobile.sale.line'].sudo().create({
                'mobile_id': mobile.id,
                'product_id': product_object.id,
                'qty': product_json['qty'],
                'price': customer.property_product_pricelist.item_ids.filtered(lambda a: a.product_tmpl_id.id == product_object.product_tmpl_id.id).fixed_price,

            })
            for tax in product_object.taxes_id:
                sale_line.write({'tax_ids':[(4,tax.id)]})
        mobile.button_confirm()
        mobile.sudo().write({
            'seller_id': session,
            'location_id': session.truck_id.id,
            'warehouse_id': warehouse_id
        })
        mobile.button_dispatch()
        mobile.sudo().write({
            'payment_method': int(payment)
        })
        mobile.make_done()
        return {'message': 'Compra realizada satifactoriamente'}

    @http.route('/api/accept_order', type="json", method=['GET'], auth='public', cors='*')
    def accept_order(self, mobile_id, latitude, longitude):
        mobile = request.env['mobile.sale.order'].sudo().search([('id', '=', int(mobile_id))])
        mobile.write({
            'assigned_latitude': latitude,
            'assigned_longitude': longitude,
        })
        mobile.button_dispatch()

    @http.route('/api/cancel', type="json", method=['GET'], auth="token", cors='*')
    def cancel_order(self, mobile_id):
        mobile = request.env['mobile.sale.order'].sudo().search([('id', '=', mobile_id)])
        if not mobile_id:
            return {'No existe este pedido'}
        mobile.cancel_order()
        return {'Pedido {} ha sido cancelado'.format(mobile.name)}

    @http.route('/api/sale/make_done', type='json', method=['GET'], auth='public', cors='*')
    def make_done(self, mobile_id, payment_id):
        mobile_order = request.env['mobile.sale.order'].sudo().search([('id', '=', mobile_id)])
        logging.getLogger().error(mobile_order.customer_id.display_name)

        mobile_order.write({
            'payment_method': payment_id,
        })
        mobile_order.make_done()
        return {'mobile_order', mobile_order.name}

    @http.route('/api/redo_truck', type='json', method=['GET'], auth='token', cors='*')
    def redo_truck(self, session, orderId):
        session = request.env['truck.session'].sudo().search([('id', '=', session)])
        session.sudo().write({
            'is_present': False
        })
        if not orderId:
            order = request.env['mobile.sale.order'].sudo().search([('id', '=', orderId)])
            order.sudo().write({
                'seller_id': None,
                'state': 'confirm'

            })

    @http.route('/api/set_active', type='json', method=['GET'], auth='token', cors='*')
    def set_active(self, session):
        session = request.env['truck.session'].sudo().search([('id', '=', session)])
        session.sudo().write({
            'is_present': True
        })

    @http.route('/api/mobile_orders', type="json", method=['GET'], auth='token', cors='*')
    def get_orders(self, latitude, longitude, session):
        order_active = request.env['mobile.sale.order'].search(
            [('seller_id.id', '=', session), ('state', 'in', ('assigned', 'onroute'))])

        session_active = request.env['truck.session'].sudo().search([('id', '=', session)])
        if not order_active and session_active.is_present:
            env = request.env['mobile.sale.order'].sudo().search([('state', '=', 'confirm')])
            session = request.env['truck.session'].sudo().search([('id', '=', session)])
            truck = request.env['stock.location'].sudo().search([('id', '=', session.truck_id.id)])
            truck_stock = request.env['stock.quant'].sudo().search([('location_id', '=', truck.id)])
            stock_array = []
            now = datetime.datetime.now
            respond = []
            distance = []
            _logger = logging.getLogger(__name__)
            gmaps = googlemaps.Client(key='AIzaSyBmphvpedTCBZvDDW3MEVknSowfl7O-v3Y')
            ##Get Stock of truck
            for stock in truck_stock:
                if stock.quantity > 0:
                    stock_array.append({
                        'Product_id': stock.product_id.id,
                        'Product': stock.product_id.display_name,
                        'Qty': stock.quantity
                    })
            for res in env:
                url_google = "https://maps.googleapis.com/maps/api/directions/json?origin={},{}&destination={},{}&key=AIzaSyBmphvpedTCBZvDDW3MEVknSowfl7O-v3Y".format(
                    latitude, longitude, res.customer_id.partner_latitude, res.customer_id.partner_longitude)
                respond_google = requests.request("GET", url=url_google)
                logging.getLogger().error(res.display_name)
                logging.getLogger().error(url_google)
                json_data = json.loads(respond_google.text)
                distance_text = json_data['routes'][0]["legs"][0]['distance']['text']
                distance_value = json_data['routes'][0]["legs"][0]['distance']['value'] / 1000
                logging.error(stock_array)
                if self.compare_list(res.mapped('mobile_lines').mapped('product_id').mapped('id'),
                                     [stock['Product_id'] for stock in stock_array]):
                    logging.error("Llega aqui")
                    respond.append({
                        'Order_Id': res.id,
                        'Order_Name': res.name,
                        'Distance_Text': distance_text,
                        'Distance_Value': self.round_distance(float(distance_value))
                    })
                else:
                    logging.error("Llega aca")
                    continue
            list_sort_by_dis = sorted(respond, key=lambda i: i['Distance_Value'])
            logging.getLogger().error(list_sort_by_dis)
            if len(list_sort_by_dis) > 0:
                mobile_order = request.env['mobile.sale.order'].sudo().search(
                    [('id', '=', list_sort_by_dis[0]['Order_Id'])])
                warehouse = request.env['stock.warehouse'].sudo().search([])
                warehouse_id = 0
                for ware in warehouse:
                    if truck.id in ware.mapped('truck_ids').mapped('id'):
                        warehouse_id = ware.id
                mobile_order.sudo().write({
                    'seller_id': session,
                    'location_id': truck.id,
                    'warehouse_id': warehouse_id,
                    'state': 'assigned'
                })
            order_app = {}
            order_active_2 = request.env['mobile.sale.order'].search(
                [('seller_id.id', '=', session.id), ('state', 'in', ('confirm','assigned'))])
            logging.getLogger().error('Order {}'.format(order_active_2.name))
            if order_active_2:
                order_app = {
                    'Order_Id': str(order_active_2.id),
                    'Order_Name': order_active_2.name,
                }
            return order_app
        else:
            order_app = {
                'Order_Id': str(order_active.id),
                'Order_Name': order_active.name
            }
            return order_app

    @http.route('/api/my_orders', type='json', method=['GET'], auth='token', cors='*')
    def get_my_orders(self, employee):
        session = request.env['truck.session'].sudo().search([('employee_id', '=', employee)])
        env = request.env['mobile.sale.order'].sudo().search(
            [('seller_id', 'in', session.mapped('id')), ('state', '=', 'done')],order="date_done desc")
        result = []
        for res in env:
            result.append({
                "id": res.id,
                "name": res.name,
                "customerName": res.customer_id.display_name,
                "address": res.customer_id.street,
                "total": res.total_sale
            })
        return result

    @http.route('/api/order', type='json', method=['GET'], auth='token', cors='*')
    def get_order(self, latitude, longitude, id):
        if id:
            order = request.env['mobile.sale.order'].sudo().search([('id', '=', int(id))])
            respond = []
            url_google = "https://maps.googleapis.com/maps/api/directions/json?origin={},{}&destination={},{}&key=AIzaSyBmphvpedTCBZvDDW3MEVknSowfl7O-v3Y".format(
                latitude, longitude, order.customer_id.partner_latitude, order.customer_id.partner_longitude)
            respond_google = requests.request("GET", url=url_google)
            json_data = json.loads(respond_google.text)
            logging.getLogger().error(json_data)

            distance_text = json_data['routes'][0]['legs'][0]['distance']['text']
            lines = []
            for line in order.mobile_lines:
                lines.append({
                    "id": line.id,
                    "productId": line.product_id.id,
                    "productName": line.product_id.name,
                    "priceUnit": line.price,
                    "qty": line.qty
                })
            respond.append({
                "OrderId": order.id,
                "OrderName": order.name,
                "Distance": distance_text,
                "ClientName": order.customer_id.display_name,
                "ClientAddress": order.customer_id.street,
                "ClientLatitude": order.customer_id.partner_latitude,
                "ClientLongitude": order.customer_id.partner_longitude,
                "Lines": lines,
                'State': order.state,
                "Total": order.total_sale
            })
            return respond
        else:
            return []

    @http.route('/api/paymentmethod', type='json', method=['GET'], auth='token', cors='*')
    def get_paymeth_method(self):
        respond = request.env['pos.payment.method'].sudo().search([])
        result = []

        for res in respond:
            result.append({
                'Id': res.id,
                'Name': res.name
            })

        return result

    def compare_list(self, array1, array2):
        return functools.reduce(lambda x, y: x and y, map(lambda p, q: p == q,
                                                          array1,
                                                          array2), True)

    def round_distance(self, value):
        value_separate = str(value).split('.')
        logging.getLogger().error(value_separate[-1])
        if int(value_separate[-1][0]) >= 5:

            return math.ceil(value)
        else:
            return round(value, 1)

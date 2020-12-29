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
            product_json = json.load(product)
            line = request.env['mobile.sale.line'].sudo().create({
                'product_id': product_json['id'],
                'price': product_json['price'],
                'state': 'progress',
                'qty': product_json['qty'],
                'mobile_id': sale_order.id
            })

        return {'message': 'Compra realizada satifactoriamente', 'sale_order': sale_order.id}

    @http.route('/api/create_mobile', type='json', method=['POST'], auth='public', cors='*')
    def create_sale(self, customer_id, product_ids,session,payment):
        customer = request.env['res.partner'].sudo().search([('id', '=', customer_id)])
        session = request.env['truck.session'].sudo().search([('id','=',session)])
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
            product_object = request.env['product.product'].sudo().search([('id','=',int(product_json['id']))])
            sale_line = request.env['mobile.sale.line'].sudo().create({
                'mobile_id': mobile.id,
                'product_id': product_object.id,
                'qty': product_json['qty'],
                'price': product_json['price']
            })
        mobile.button_confirm()
        mobile.sudo().write({
            'seller_id': session,
            'location_id': session.truck_id.id,
            'warehouse_id': warehouse_id
        })
        mobile.button_dispatch()
        mobile.sudo().write({
            'payment_method':int(payment)
        })
        mobile.make_done()
        return {'message': 'Compra realizada satifactoriamente'}

    @http.route('/api/confirm_sale', type="json", method=['GET'], auth="token", cors="*")
    def confirm_sale(self, order_id):
        mobile = request.env['mobile.sale.order'].sudo().search([('id', '=', int(order_id))])
        mobile.button_confirm()
        return {"Pedido Confirmado"}

    @http.route('/api/sale/take_saleman', type="json", method=['GET'], auth='public', cors='*')
    def take_saleman(self, mobile_id, session):
        mobile_order = request.env['mobile.sale.order'].search([('id', '=', mobile_id)])
        truck_session = request.env['truck.session'].sudo().search([('id', '=', int(session))])

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
    def make_done(self, mobile_id, payment_id):
        mobile_order = request.env['mobile.sale.order'].sudo().search([('id', '=', mobile_id)])

        mobile_order.write({
            'payment_method': payment_id,
        })
        mobile_order.make_done()
        return {'mobile_order', mobile_order.name}

    @http.route('/api/redo_truck',type='json',method=['GET'],auth='token',cors='*')
    def redo_truck(self,session,orderId):
        session = request.env['truck.session'].sudo().search([('id','=',session)])
        session.sudo().write({
            'is_present':False
        })
        if orderId == False:
            order = request.env['mobile.sale.order'].sudo().search([('id','=',orderId)])
            order.sudo().write({
                'seller_id':None,
                'state':'confirm'

            })

    @http.route('/api/set_active',type='json',method=['GET'],auth='token',cors='*')
    def set_active(self,session):
        session = request.env['truck.session'].sudo().search([('id','=',session)])
        session.sudo().write({
            'is_present':True
        })

    @http.route('/api/mobile_orders', type="json", method=['GET'], auth='token', cors='*')
    def get_orders(self, latitude, longitude, session):
        order_active = request.env['mobile.sale.order'].search(
            [('seller_id.id', '=', session), ('state', '=', 'onroute')])
        session_active = request.env['truck.session'].sudo().search([('id','=',session)])
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
                logging.getLogger().error(url_google)
                json_data = json.loads(respond_google.text)
                distance_text = json_data['routes'][0]["legs"][0]['distance']['text']
                distance_value = json_data['routes'][0]["legs"][0]['distance']['value'] / 1000
                if self.compare_list(res.mapped('mobile_lines').mapped('product_id').mapped('id'),
                                     [stock['Product_id'] for stock in stock_array]):
                    respond.append({
                        'Order_Id': res.id,
                        'Order_Name': res.name,
                        'Distance_Text': distance_text,
                        'Distance_Value': self.round_distance(float(distance_value))
                    })
                else:
                    continue
            list_sort_by_dis = sorted(respond, key=lambda i: i['Distance_Value'])
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
                    'warehouse_id': warehouse_id
                })
                mobile_order.button_dispatch()
            order_app = {}
            order_active_2 = request.env['mobile.sale.order'].search(
                [('seller_id.id', '=', session.id), ('state', '=', 'onroute')])
            if order_active_2:
                order_app = {
                    'Order_Id': str(order_active_2.id),
                    'Order_Name': order_active_2.name
                }
            return order_app
        else:
            order_app = {
                'Order_Id': str(order_active.id),
                'Order_Name': order_active.name
            }
            return order_app

    @http.route('/api/my_orders', type='json', method=['GET'], auth='token', cors='*')
    def get_my_orders(self, session, latitude, longitude):
        env = request.env['mobile.sale.order'].sudo().search(
            [('seller_id', '=', int(session)), ('state', '=', 'onroute')])
        respond = []
        _logger = logging.getLogger(__name__)
        _logger.error(latitude)
        gmaps = googlemaps.Client(key='AIzaSyByqie1H_p7UUW2u6zTIynXgmvJUdIZWx0')

        now = datetime.datetime.now()

        for res in env:
            respond = []
            description = ''
            array_srt_des = []
            array_des = []
            s = ' '
            now = datetime.datetime.now()
            dir = gmaps.directions((latitude, longitude),
                                   (res.customer_id.partner_latitude, res.customer_id.partner_longitude),
                                   mode="driving",
                                   departure_time=now)
            for product in res.mobile_lines:
                if product.qty > 1:
                    array_srt_des.append('{} {}s'.format(product.qty, product.product_id.name))
                    array_des.append({
                        'Id': product.id,
                        'ImageUrl': '/web/image?model=product.template&field:image_1920&id={}'.format(
                            product.product_id.product_tmpl_id.id),
                        'Product_Id': product.product_id.id,
                        'ProductName': product.product_id.name,
                        'Qty': product.qty,
                        'PriceUnit': product.price
                    })
                else:
                    array_srt_des.append('{} {}'.format(product.qty, product.product_id.name))
                    array_des.append({
                        'Id': product.id,
                        'ImageUrl': '/web/image?model=product.product&field:image_1920&id={}'.format(
                            product.product_id.id),
                        'Product_Id': product.product_id.id,
                        'ProductName': product.product_id.name,
                        'Qty': product.qty,
                        'PriceUnit': product.price
                    })
            description = s.join(array_srt_des)
            if res.address_id:
                respond.append({
                    'id': str(res.id),
                    'OrderName': res.name,
                    'ClientName': res.address_id.display_name,
                    'ClientAddress': res.address_id.street,
                    'ClientLatitude': res.address_id.partner_latitude,
                    'ClientLongiutude': res.address_id.partner_longitude,
                    'ClientPhone': res.address_id.mobile,
                    'ShortDescription': description,
                    'Distance': dir[0]['legs'][0]['distance']['text'] if len(dir) > 0 else '',
                    'Description': array_des,
                    'Total': res.total_sale
                })
            else:
                respond.append({
                    'id': str(res.id),
                    'OrderName': res.name,
                    'ClientName': res.customer_id.display_name,
                    'ClientAddress': res.customer_id.street,
                    'ClientLatitude': res.customer_id.partner_latitude,
                    'ClientLongiutude': res.customer_id.partner_longitude,
                    'ClientPhone': res.customer_id.mobile,
                    'ShortDescription': description,
                    'Distance': dir[0]['legs'][0]['distance']['text'] if len(dir) > 0 else '',
                    'Description': array_des,
                    'Total': res.total_sale
                })
        list_sort_by_dis = sorted(respond, key=lambda i: i['Distance'], reverse=True)
        _logger.error(list_sort_by_dis)
        return list_sort_by_dis

    @http.route('/api/order', type='json', method=['GET'], auth='token', cors='*')
    def get_order(self, latitude, longitude, id):
        order = request.env['mobile.sale.order'].sudo().search([('id', '=', int(id))])
        respond = []
        url_google = "https://maps.googleapis.com/maps/api/directions/json?origin={},{}&destination={},{}&key=AIzaSyBmphvpedTCBZvDDW3MEVknSowfl7O-v3Y".format(
            latitude, longitude, order.customer_id.partner_latitude, order.customer_id.partner_longitude)
        logging.getLogger().error(url_google)
        respond_google = requests.request("GET",url=url_google)
        json_data = json.loads(respond_google.text)
        logging.getLogger().error(json_data)

        distance_text = json_data['routes'][0]['legs'][0]['distance']['text']
        lines = []
        for line in order.mobile_lines:
            lines.append({
                "id":line.id,
                "productId": line.product_id.id,
                "productName":line.product_id.name,
                "priceUnit":line.price,
                "qty":line.qty
            })
        respond.append({
            "OrderId":order.id,
            "OrderName":order.name,
            "Distance":distance_text,
            "ClientName":order.customer_id.display_name,
            "ClientAddress":order.customer_id.street,
            "ClientLatitude":order.customer_id.partner_latitude,
            "ClientLongitude":order.customer_id.partner_longitude,
            "Lines":lines,
            "Total":order.total_sale
        })
        return respond

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

from odoo import http
from odoo.http import request
import datetime
import logging
import googlemaps


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

    @http.route('/api/create_mobile', type='json', method=['POST'], auth='public', cors='*')
    def create_sale(self, customer_id, product_ids):
        customer = request.env['res.partner'].search([('id', '=', customer_id)])
        mobile = request.env['mobile.sale.order'].create({
            'customer_id': customer.id,
        })
        for product in product_ids:
            request.env['mobile.sale.line'].create({
                'product_id': product.id,
                'qty': product.qty,
                'price': product.price
            })
        mobile.button_confirm()
        return {'message': 'Compra realizada satifactoriamente'}

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

    @http.route('/api/mobile_orders', type="json", method=['GET'], auth='token', cors='*')
    def get_orders(self, latitude, longitude):
        env = request.env['mobile.sale.order'].sudo().search([('state', '=', 'confirm')])
        respond = []
        _logger = logging.getLogger(__name__)
        _logger.error('Lat {} , Long {}'.format(latitude, longitude))
        gmaps = googlemaps.Client(key='AIzaSyByqie1H_p7UUW2u6zTIynXgmvJUdIZWx0')

        now = datetime.datetime.now()

        for res in env:
            description = ''
            array_srt_des = []
            array_des = []
            s = ' '

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
                    'Distance': dir[0]['legs'][0]['distance']['text'],
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
                    'Distance': dir[0]['legs'][0]['distance']['text'] if dir != None else '',
                    'Description': array_des,
                    'Total': res.total_sale
                })
        list_sort_by_dis = sorted(respond, key=lambda i: i['Distance'], reverse=True)
        return list_sort_by_dis

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
            description = ''
            array_srt_des = []
            array_des = []
            s = ' '

            dir = gmaps.directions((latitude, longitude),
                                   (res.customer_id.partner_latitude, res.customer_id.partner_longitude),
                                   mode="driving",
                                   departure_time=now)
            for product in res.mobile_lines:
                if product.qty > 1:
                    array_srt_des.append('{} {}s'.format(product.qty, product.product_id.name))
                    array_des.append({
                        'Id': product.id,
                        'ImageUrl': '/web/image?model=product.product&field:image_1920&id={}'.format(
                            product.product_id.id),
                        'Image': product.product_id.image_128,
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
                        'Image': product.product_id.image_128,
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
                    'ClientPhone': res.address_id.mobile,
                    'ClientLatitude': res.address_id.partner_latitude,
                    'ClientLongiutude': res.address_id.partner_longitude,
                    'ShortDescription': description,
                    'Distance': dir[0]['legs'][0]['distance']['text'],
                    'Description': array_des,
                    'Total': res.total_sale
                })
            else:
                respond.append({
                    'id': str(res.id),
                    'ClientName': res.customer_id.display_name,
                    'OrderName': res.name,
                    'ClientAddress': res.customer_id.street,
                    'ClientLatitude': res.customer_id.partner_latitude,
                    'ClientLongiutude': res.customer_id.partner_longitude,
                    'ClientPhone': res.customer_id.mobile,
                    'ShortDescription': description,
                    'Distance': dir[0]['legs'][0]['distance']['text'],
                    'Description': array_des,
                    'Total': res.total_sale
                })
        list_sort_by_dis = sorted(respond, key=lambda i: i['Distance'], reverse=True)
        _logger.error(list_sort_by_dis)
        return list_sort_by_dis

    @http.route('/api/paymentmethod', type='json', method=['GET'], auth='token', cors='*')
    def get_paymeth_method(self):
        respond = request.env['pos.payment.method'].sudo().search([])
        result = []

        for res in respond:
            result.append({
                'Id': str(res.id),
                'Name': res.name
            })

        return result

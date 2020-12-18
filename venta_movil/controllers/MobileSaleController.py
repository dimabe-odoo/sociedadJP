from odoo import http
from odoo.http import request
import datetime
import logging
import json
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
    def create_sale(self, customer_id, product_ids,latitude,longitude):
        customer = request.env['res.partner'].sudo().search([('id', '=', customer_id)])
        mobile = request.env['mobile.sale.order'].sudo().create({
            'state':'draft',
            'customer_id': customer.id,
        })
        for product in product_ids:
            product_json = json.loads(product)
            request.env['mobile.sale.line'].sudo().create({
                'mobile_id':mobile.id,
                'product_id': product_json['id'],
                'qty': product_json['qty'],
                'price': product_json['price']
            })
        gmaps = googlemaps.Client(key='AIzaSyByqie1H_p7UUW2u6zTIynXgmvJUdIZWx0')
        respond = self.get_mobile(mobile,gmaps,latitude,longitude)
        return {'message': 'Compra realizada satifactoriamente','result':respond}

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
            respond = self.get_mobile(res, gmaps, latitude, longitude)
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
            respond = self.get_mobile(res,gmaps,latitude,longitude)
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

    def get_mobile(self,mobile,gmaps,latitude,longitude):
        respond = []
        description = ''
        array_srt_des = []
        array_des = []
        s = ' '
        now = datetime.datetime.now()
        dir = gmaps.directions((latitude, longitude),
                               (mobile.customer_id.partner_latitude, mobile.customer_id.partner_longitude),
                               mode="driving",
                               departure_time=now)
        for product in mobile.mobile_lines:
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
        if mobile.address_id:
            respond.append({
                'id': str(mobile.id),
                'OrderName': mobile.name,
                'ClientName': mobile.address_id.display_name,
                'ClientAddress': mobile.address_id.street,
                'ClientLatitude': mobile.address_id.partner_latitude,
                'ClientLongiutude': mobile.address_id.partner_longitude,
                'ClientPhone': mobile.address_id.mobile,
                'ShortDescription': description,
                'Distance': dir[0]['legs'][0]['distance']['text'] if len(dir) > 0 else '',
                'Description': array_des,
                'Total': mobile.total_sale
            })
        else:
            respond.append({
                'id': str(mobile.id),
                'OrderName': mobile.name,
                'ClientName': mobile.customer_id.display_name,
                'ClientAddress': mobile.customer_id.street,
                'ClientLatitude': mobile.customer_id.partner_latitude,
                'ClientLongiutude': mobile.customer_id.partner_longitude,
                'ClientPhone': mobile.customer_id.mobile,
                'ShortDescription': description,
                'Distance': dir[0]['legs'][0]['distance']['text'] if len(dir) > 0 else '',
                'Description': array_des,
                'Total': mobile.total_sale
            })
        return respond
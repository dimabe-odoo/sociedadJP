from odoo import http, _
from odoo.http import request
import datetime
import logging
import json
import functools
import googlemaps
import requests
import math
from odoo.tools import date_utils
from odoo import models
from datetime import date


def verify_stock_truck_for_order(order_active, session):
    orders_with_stock = []
    for order in order_active:
        if session.user_id in order.not_accepted_truck_ids:
            continue
        else:
            # Verify Stock Truck
            truck_stock = request.env['stock.quant'].sudo().search(
                [('location_id', '=', session.truck_id.id), ('quantity', '>', 0)])
            if not truck_stock:
                continue
            for stock in truck_stock:
                if stock.product_id.id not in order.mobile_lines.mapped('product_id').ids:
                    continue
                else:
                    orders_with_stock.append(order.id)
    return orders_with_stock


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
                'price': customer.property_product_pricelist.item_ids.filtered(
                    lambda a: a.product_tmpl_id.id == product_object.product_tmpl_id.id).fixed_price,

            })
            for tax in product_object.taxes_id:
                sale_line.write({'tax_ids': [(4, tax.id)]})
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

    @http.route('/api/create_sale_order', type="json", method=['POST'], auth="token", cors='*')
    def create_sale_order(self, products, client):
        customer = request.env['res.partner'].sudo().search([('id', '=', client)])
        mobile = request.env['mobile.sale.order'].sudo().create({
            'state': 'draft',
            'customer_id': customer.id,
            'price_list_id': customer.property_product_pricelist.id
        })
        line = []
        for product in products:
            product_json = json.loads(product)
            product_object = request.env['product.product'].sudo().search([('id', '=', int(product_json['id']))])
            logging.getLogger().error(product_object.taxes_id)
            sale_line = request.env['mobile.sale.line'].sudo().create({
                'mobile_id': mobile.id,
                'product_id': product_object.id,
                'qty': product_json['qty'],
                'price': customer.property_product_pricelist.item_ids.filtered(
                    lambda a: a.product_tmpl_id.id == product_object.product_tmpl_id.id).fixed_price,

            })
            for tax in product_object.taxes_id:
                sale_line.write({'tax_ids': [(4, tax.id)]})
        mobile.button_confirm()
        return {"message": "Compra Realizada Safisfactoriamente, por favor quedar a la espera del repartidor",
                "mobileID": mobile.id}

    @http.route('/api/accept_order', type="json", method=['GET'], auth='public', cors='*')
    def accept_order(self, mobile_id, latitude, longitude, session=False):
        try:
            mobile = request.env['mobile.sale.order'].sudo().search([('id', '=', int(mobile_id))])
            session_id = request.env['truck.session'].sudo().search([('id', '=', session)])
            if not session_id:
                session_id = request.env['truck.session'].sudo().search([('user_id.id', '=', request.env.uid)])
            mobile.write({
                'seller_id': session_id.id,
                'warehouse_id': session_id.warehouse_id.id,
                'location_id': session_id.truck_id.id,
                'assigned_latitude': latitude,
                'assigned_longitude': longitude,
            })
            mobile.button_dispatch()
            return {"message": "Pedido Aceptado"}
        except Exception as e:
            return {"message": "Error"}

    @http.route('/api/repeat_order', type="json", method=["GET"], auth="token", cors="*")
    def repeat_order(self, id):
        mobile = request.env['mobile.sale.order'].search([('id', '=', id)])
        if mobile:
            new_mobile = mobile.copy()
            return {"message": "Nuevo pedido creado a partir de uno ya finalizado", 'mobileId': new_mobile.id}

    @http.route('/api/cancel', type="json", method=['GET'], auth="token", cors='*')
    def cancel_order(self, mobile_id, truck):
        try:
            mobile = request.env['mobile.sale.order'].sudo().search([('id', '=', mobile_id)],limit=1)
            truck = request.env['truck.session'].sudo().search(
                [('truck_id.name', '=', truck), ('is_present', '=', True)])
            if not mobile_id:
                return {'No existe este pedido'}
            mobile[0].not_accepted_truck_ids = [(4, request.env.uid)]
            return {"message": 'Pedido {} ha sido cancelado'.format(mobile.name)}
        except Exception as e:
            return {"message": "Error"}

    @http.route('/api/sale/make_done', type='json', method=['GET'], auth='public', cors='*')
    def make_done(self, mobile_id, payment_id):
        try:
            mobile_order = request.env['mobile.sale.order'].sudo().search([('id', '=', mobile_id)])
            logging.getLogger().error(mobile_order.customer_id.display_name)

            mobile_order.write({
                'payment_method': payment_id,
            })
            mobile_order.make_done()
            return {"message": "Pedido Entregado correctamente"}
        except Exception as e:
            return {"message": "Error de comunicacion"}

    @http.route('/api/redo_truck', type='json', method=['GET'], auth='token', cors='*')
    def redo_truck(self, session, orderId):
        try:
            session_obj = request.env['truck.session'].sudo().search([('id', '=', session)])
            session_obj.sudo().write({
                'is_present': False
            })
            if orderId:
                order = request.env['mobile.sale.order'].sudo().search([('id', '=', orderId)])
                order.sudo().write({
                    'seller_id': None,
                    'state': 'confirm',
                    'warehouse_id': None,
                    'location_id': None
                })
            else:
                order = request.env['mobile.sale.order'].sudo().search(
                    [('location_id.id', '=', session_obj.truck_id.id), ('state', '!=', 'done')])
                order.sudo().write({
                    'seller_id': None,
                    'state': 'confirm',
                    'warehouse_id': None,
                    'location_id': None
                })
            return {"message": "Sesion Desactivada y Pedido liberado"}
        except Exception as e:
            return {"message": "Error"}

    @http.route('/api/set_active', type='json', method=['GET'], auth='token', cors='*')
    def set_active(self, session):
        try:
            session = request.env['truck.session'].sudo().search([('id', '=', session)])
            session.sudo().write({
                'is_present': True
            })
            return {"message": "Sesion Activa"}
        except Exception as e:
            return {"message": "Error"}

    @http.route('/api/mobile_orders', type="json", method=['GET'], auth='token', cors='*')
    def get_orders(self, latitude, longitude, session):
        order_active = request.env['mobile.sale.order'].sudo().search(
            [('seller_id', '=', False), ('state', '=', 'confirm')])
        session = request.env['truck.session'].sudo().search([('id', '=', session)])
        order_assigned = request.env['mobile.sale.order'].search(
            [('seller_id', '=', session.id), ('state', 'not in', ['done', 'cancel', 'draft'])]).filtered(lambda x: request.env.uid not in x.not_accepted_truck_ids.ids)
        if order_active and not order_assigned:
            order_with_stock = request.env['mobile.sale.order'].sudo().search(
                [('id', 'in', verify_stock_truck_for_order(order_active, session))])
            if len(order_with_stock) == 1 and not order_with_stock.not_accepted_truck_ids:
                order_with_stock.write({
                    'seller_id': session.id,
                    'warehouse_id': session.warehouse_id.id,
                    'location_id': session.truck_id.id,
                    'assigned_latitude': latitude,
                    'assigned_longitude': longitude,
                })
                return self.get_order(latitude,
                                      longitude, order_with_stock.id)
            else:
                orders = []
                for order in order_with_stock:
                    gmaps = googlemaps.Client(key='AIzaSyBmphvpedTCBZvDDW3MEVknSowfl7O-v3Y')
                    url_google = "https://maps.googleapis.com/maps/api/directions/json?origin={},{}&destination={},{}&key=AIzaSyBmphvpedTCBZvDDW3MEVknSowfl7O-v3Y".format(
                        latitude, longitude, order.customer_id.partner_latitude, order.customer_id.partner_longitude)
                    google_resp = requests.request("GET", url=url_google)
                    json_google = json.loads(google_resp.text)
                    if json_google['status'] != 'OK':
                        continue
                    else:
                        orders.append({
                            "order": order,
                            "distance_value": json_google['routes'][0]["legs"][0]['distance']['value']
                        })
                orders_sorted_by_dist = sorted(orders, key=lambda i: i['distance_value'])
                orders_sorted_by_dist[0]['order'].write({
                    'seller_id': session.id,
                    'warehouse_id': session.warehouse_id.id,
                    'location_id': session.truck_id.id,
                    'assigned_latitude': latitude,
                    'assigned_longitude': longitude,
                })
                return self.get_order(latitude,
                                      longitude,
                                      orders_sorted_by_dist[0]['order'].id)
        elif order_assigned and request.env.uid not in order_assigned.not_accepted_truck_ids.ids:
            return self.get_order(latitude, longitude, order_assigned.id)

    @http.route('/api/my_orders', type='json', method=['GET'], auth='token', cors='*')
    def get_my_orders(self, employee):
        session = request.env['truck.session'].sudo().search([('employee_id', '=', employee)])
        env = request.env['mobile.sale.order'].sudo().search(
            [('seller_id', 'in', session.mapped('id')), ('state', '=', 'done')], order="date_done desc")

        result = []
        for res in env:
            date = res.finish_date.strftime('%Y-%m-%d')
            if datetime.datetime.now().strftime('%Y-%m-%d') == date:
                lines = []
                for line in res.mobile_lines:
                    lines.append({
                        "id": line.id,
                        "productId": line.product_id.id,
                        "productName": line.product_id.name,
                        "priceUnit": line.price,
                        "qty": line.qty
                    })
                description = ','.join(f'Producto : {line["productName"]} Cantidad : {line["qty"]}' for line in lines)
                result.append({
                    "OrderId": res.id,
                    "OrderName": res.name if res.name else '',
                    "ClientName": res.customer_id.display_name,
                    "ClientAddress": res.customer_id.street,
                    "ClientLatitude": res.customer_id.partner_latitude,
                    "ClientLongitude": res.customer_id.partner_longitude,
                    'State': res.state,
                    "Total": int(res.total_sale),
                    "orderDescription": description
                })
        return result

    @http.route('/api/client_orders', type='json', method=['GET'], auth='token', cors='*')
    def get_client_orders(self, partner_id):
        mobile_sale_order = request.env['mobile.sale.order'].search([('customer_id', '=', partner_id)])
        my_orders = []
        for mobile in mobile_sale_order:
            my_orders.append({
                'id': mobile.id,
                'name': mobile.name if mobile.name else '',
                'state': self.selection_to_string('mobile.sale.order', 'state', mobile.state),
            })
        return my_orders

    @http.route('/api/order', type='json', method=['GET'], auth='token', cors='*')
    def get_order(self, latitude, longitude, id):
        try:
            return self.get_order_dict(latitude, longitude, id)
        except Exception as e:
            return {'message': "Error en Comunicacion"}

    def get_order_dict(self, latitude, longitude, id):
        if id:
            order = request.env['mobile.sale.order'].sudo().search([('id', '=', int(id))])
            respond = []
            url_google = "https://maps.googleapis.com/maps/api/directions/json?origin={},{}&destination={},{}&key=AIzaSyBmphvpedTCBZvDDW3MEVknSowfl7O-v3Y".format(
                latitude, longitude, order.customer_id.partner_latitude, order.customer_id.partner_longitude)
            respond_google = requests.request("GET", url=url_google)
            json_data = json.loads(respond_google.text)
            if json_data['status'] != 'ZERO_RESULTS':
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
                "OrderName": order.name if order.name else '',
                "Distance": distance_text,
                "ClientName": order.customer_id.display_name,
                "ClientAddress": order.customer_id.street,
                "ClientLatitude": order.customer_id.partner_latitude,
                "ClientLongitude": order.customer_id.partner_longitude,
                "Lines": lines,
                'State': order.state,
                "Total": order.total_sale
            })
            return {"message": f"Orden {'Asignada' if order.state == 'assigned' else 'En Ruta'}", "order": respond}
        else:
            return []

    @http.route('/api/get_client_order', type='json', method=['GET'], auth='token', cors='*')
    def get_order_client(self, id):
        mobile_order = request.env['mobile.sale.order'].sudo().search([('id', '=', id)])
        if mobile_order:
            mobile_order_dict = self.odoo_obj_to_dict('mobile.sale.order', id)
            lines = []
            for line in mobile_order.mobile_lines:
                line_dict = self.odoo_obj_to_dict('mobile.sale.line', line.id)
                lines.append(line_dict)
            mobile_order_dict['product_lines'] = lines
            mobile_order_dict['spanish_state'] = self.selection_to_string('mobile.sale.order', 'state',
                                                                          mobile_order.state)
            return mobile_order_dict

    def odoo_obj_to_dict(self, model, id):
        odoo_object = request.env[model].sudo().search([('id', '=', id)])
        raw_data = odoo_object.read()
        json_data = json.dumps(raw_data, default=date_utils.json_default)
        json_dict = json.loads(json_data)
        return json_dict[0]

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

    def selection_to_string(self, model, field_name, field_value):
        return _(dict(request.env[model].fields_get(allfields=[field_name])[field_name]['selection'])[field_value])

    def get_total(self, order):
        total_untax = []
        total_tax = []
        for line in order.mobile_lines:
            total_untax.append(line.price * line.qty)
            for tx in line.tax_ids:
                total_tax.append((tx.amount / 100) * line.price * line.qty)
        return sum(total_untax) + sum(total_tax)

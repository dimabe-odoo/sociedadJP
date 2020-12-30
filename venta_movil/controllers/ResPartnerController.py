from odoo import http
from odoo.http import request
import datetime
import logging
import googlemaps


class ResPartnerController(http.Controller):


    @http.route('/api/clients', type='json', method=['GET'], auth='token', cors='*')
    def get_clients(self, truck):
        respond = request.env['res.partner'].sudo().search([])
        location = request.env['stock.location'].sudo().search([('name', '=', truck)])
        stock = request.env['stock.quant'].sudo().search([('location_id', '=', location.id)])

        result = []
        now = datetime.datetime.now()
        _logger = logging.getLogger(__name__)
        _logger.error(stock.mapped('product_id'))
        for res in respond:
            another = []
            for c in res.sudo().child_ids:
                price_another = []
                for pr in res.sudo().property_product_pricelist.item_ids:
                    product = request.env['product.product'].sudo().search(
                        [('product_tmpl_id', '=', pr.product_tmpl_id.id)])
                    _logger.error(product)
                    stock_product = stock.filtered(lambda a: a.product_id.id == product.id)
                    _logger.error(stock_product.mapped('taxes_id').mapped('amount'))
                    price_another.append({
                        'Product_Id': pr.product_tmpl_id.id,
                        'Product_Name': pr.product_tmpl_id.name,
                        'isCat': True if 'Catalítico' in pr.product_tmpl_id.display_name else False,
                        'Stock': stock_product.quantity,
                        'Price': pr.fixed_price
                    })
                another.append({
                    'Id': str(res.id),
                    'Name': c.name,
                    'Address': c.street,
                    'Latitude': c.partner_latitude,
                    'Longitude': c.partner_longitude,
                    'Phone': c.mobile,
                    'PriceList': price_another
                })
            price = []
            for pr in res.sudo().property_product_pricelist.item_ids:
                product = request.env['product.product'].sudo().search(
                    [('product_tmpl_id', '=', pr.product_tmpl_id.id)])
                _logger.error(product)
                stock_product = stock.filtered(lambda a: a.product_id.id == product.id)
                _logger.error(stock_product)
                taxes_amount = (int(sum(product.mapped('taxes_id').mapped('amount'))) / 100) + 1
                price.append({
                    'Product_Id': pr.product_tmpl_id.id,
                    'Product_Name': pr.product_tmpl_id.name,
                    'isCat': True if 'Catalítico' in pr.product_tmpl_id.display_name else False,
                    'is_Dist':True if 'Descuento' in pr.product_tmpl_id.display_name or 'Discount' in pr.product_tmpl_id.display_name else False,
                    'Stock': stock_product.quantity,
                    'Price': pr.fixed_price * taxes_amount
                })

            result.append({
                'Id': str(res.id),
                'Name': res.name,
                'Address': res.street,
                'Latitude': res.partner_latitude,
                'Longitude': res.partner_longitude,
                'Phone': res.mobile,
                'AnotherDirection': another,
                'PriceList': price
            })
        return result

from odoo.http import request


def get_prices(client_id, truck):
    client = request.env['res.partner'].sudo().search([('id', '=', client_id)])
    result = []
    location = request.env['stock.location'].sudo().search([('name', '=', truck)])
    stock = request.env['stock.quant'].sudo().search([('location_id', '=', location.id)])
    for pr in client.sudo().property_product_pricelist.item_ids:
        product = request.env['product.product'].sudo().search(
            [('product_tmpl_id', '=', pr.product_tmpl_id.id)])
        stock_product = stock.filtered(lambda a: a.product_id.id == product.id)
        taxes_amount = (int(sum(product.mapped('taxes_id').mapped('amount'))) / 100) + 1
        if pr.product_tmpl_id.categ_id.id not in (7, 5):
            result.append({
                'product_id': pr.product_tmpl_id.id,
                'product_name': pr.product_tmpl_id.name,
                'isCat': True if 'Catalítico' in pr.product_tmpl_id.display_name else False,
                'Stock': stock_product.quantity,
                'Price': pr.fixed_price
            })
    for coupon in request.env['product.product'].sudo().search([('categ_id', '=', 7)]):
        result.append({
            'product_id': coupon.product_tmpl_id.id,
            'product_name': coupon.product_tmpl_id.name,
            'is_Dist': True if 'Descuento' in coupon.product_tmpl_id.display_name or 'Discount' in coupon.product_tmpl_id.display_name else False,
            'Stock': 1,
            'Price': coupon.list_price
        })
    for cil in request.env['product.product'].sudo().search([('categ_id', '=', 5)]):
        stock_quant = request.env['stock.quant'].sudo().search([('location_id.id','=',location.id),('product_id.id','=',cil.id)])
        result.append({
            'product_id': cil.product_tmpl_id.id,
            'product_name': cil.product_tmpl_id.name,
            'isCil': True,
            'Stock': stock_quant.quantity,
            'Price': cil.list_price
        })
    return result

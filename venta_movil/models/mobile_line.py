from odoo import fields, models, api


class MobileSaleLine(models.Model):
    _name = 'mobile.sale.line'

    reference = fields.Char('Referencia', rel='mobile_id.name')

    product_id = fields.Many2one('product.product', 'Producto')

    loan_qty = fields.Integer('Prestamo')

    price = fields.Monetary('Precio')

    state = fields.Selection([('progress', 'En Progeso'), ('done', 'Hecha')], default='progress')

    qty = fields.Integer('Cantidad')

    currency_id = fields.Many2one('res.currency', 'Moneda',
                                  default=lambda self: self.env['res.currency'].search([('name', '=', 'CLP')]))

    mobile_id = fields.Many2one('mobile.sale.order', auto_join=True)

    subtotal = fields.Monetary('SubTotal')

    @api.onchange('product_id')
    def onchange_product_id(self):
        price = 0
        for item in self.mobile_id.price_list_id.item_ids:
            if item.product_tmpl_id.id == self.product_id.id:
                price = item.fixed_price
        self.price = price

    @api.onchange('qty')
    def onchange_qty(self):
        for item in self:
            if item.mobile_id.state != 'done':
                if item.qty > 0:
                    stock = self.env['stock.quant'].search(
                        [('location_id', '=', self.mobile_id.warehouse_id.lot_stock_id.id),
                         ('product_id', '=', item.product_id.id)])
                    if stock.quantity < 0:
                        raise models.ValidationError('No tiene suficiente stock de este producto')
                    else:
                        item.write({
                            'subtotal':(item.price * item.qty)
                        })

    @api.onchange('loan_qty')
    def onchange_loan_qty(self):
        if self.loan_qty > self.qty:
            raise models.ValidationError('La cantidad a prestar no puede ser mayor a la cantidad a vender')

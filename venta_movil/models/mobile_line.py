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

    subtotal = fields.Monetary('Subtotal',compute='compute_subtotal')

    tax_ids = fields.Many2many('account.tax', string='Impuestos')

    def compute_subtotal(self):
        for item in self:
            item.subtotal = item.price * item.qty


    @api.onchange('product_id')
    def onchange_product_id(self):
        price = 0
        for item in self.mobile_id.price_list_id.item_ids:
            if item.product_tmpl_id.id == self.product_id.id:
                price = item.fixed_price
        self.price = price
        self.tax_ids = self.product_id.taxes_id

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

    @api.onchange('loan_qty')
    def onchange_loan_qty(self):
        if self.loan_qty > self.qty:
            raise models.ValidationError('La cantidad a prestar no puede ser mayor a la cantidad a vender')


    @api.model
    def write(self,values):
        if values['qty'] == 0:
            raise models.UserError('No puede crear pedido con cantidad 0')
        if 'loan_qty' in  values.keys():
            if values['loan_qty'] > values['qty']:
                raise models.UserError('La cantidad a prestar no puede ser mayor a la cantidad a vender')
        return super(MobileSaleLine,self).write(values)

    @api.model
    def create(self, values):
        if values['qty'] == 0:
            raise models.UserError('No puede crear pedido con cantidad 0')
        if values['loan_qty']:
            if values['loan_qty'] > values['qty']:
                raise models.UserError('La cantidad a prestar no puede ser mayor a la cantidad a vender')
        return super(MobileSaleLine, self).create(values)
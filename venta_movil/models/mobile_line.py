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


    @api.onchange('product_id')
    def onchange_product_id(self):
        price = self.mobile_id.price_list_id.filtered(lambda a: a.product_tmpl_id.id == a.product_id.id).price
        self.price = price

    @api.onchange('loan_qty')
    def onchange_loan_qty(self):
        if self.loan_qty > self.qty:
            raise models.ValidationError('La cantidad a prestar no puede ser mayor a la cantidad a vender')
        
from odoo import fields,models,api

class MobileSaleLine(models.Model):
    _name = 'mobile.sale.line'

    reference = fields.Char('Referencia',ref='mobile_id.name')

    product_id = fields.Many2one('product.product','Producto')

    price = fields.Monetary('Precio')

    state = fields.Selection([('progress','En Progeso'),('done','Hecha')],default='progress')

    qty = fields.Integer('Cantidad')

    currency_id = fields.Many2one('res.currency','Moneda',default=_default_currency)

    mobile_id = fields.Many2one('mobile.sale.order',auto_join=True)

    def _default_currency(self):
        return self.env['res.currency'].search([('name','=','CLP')])
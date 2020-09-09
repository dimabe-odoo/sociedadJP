from odoo import fields,models,api

class MobileSaleLine(models.Model):
    _name = 'mobile.sale.line'

    reference = fields.Char('Referencia')

    product_id = fields.Many2one('Producto')

    price = fields.Float('Precio')

    state = fields.Selection([('progress','En Progeso'),('done','Hecha')])

    qty = fields.Integer('Cantidad')

    mobile_id = fields.Many2one('mobile.sale.order')
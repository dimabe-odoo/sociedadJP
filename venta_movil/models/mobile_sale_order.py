from odoo import fields, models, api


class ModileSaleOrder(models.Model):
    _name = 'mobile.sale.order'

    name = fields.Char('Nombre')

    state = fields.Selection([('progress','En Progeso'),('done','Hecha')])

    customer_id = fields.Many2one('res.partner','Cliente')

    saleman_id = fields.Many2one('res.partner','Vendedor')

    date_done = fields.Datetime('Fecha de entrega')

    product_id = fields.Many2one('product_id','Producto')

    sale_id = fields.Many2one('sale.order','Venta Interna')
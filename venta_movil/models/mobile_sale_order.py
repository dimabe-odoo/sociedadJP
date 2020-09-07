from odoo import fields, models, api


class ModileSaleOrder(models.Model):
    _name = 'mobile.sale.order'

    name = fields.Char('Nombre')

    state = fields.Selection([('progress','En Progeso'),('done','Hecha')])

    customer_id = fields.Many2one('res.partner','Cliente')

    saleman_id = fields.Many2one('res.partner','Vendedor')

    date_done = fields.Datetime('Fecha de entrega')

    product_id = fields.Many2many('product.product','Producto')

    total_sale = fields.Float('Total')

    sale_id = fields.Many2one('sale.order','Venta Interna')

    location_id = fields.Many2one('stock.location','Ubicacion')

    is_loan = fields.Boolean('Es Prestamo')
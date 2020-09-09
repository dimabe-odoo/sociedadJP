from odoo import fields, models, api


class ModileSaleOrder(models.Model):
    _name = 'mobile.sale.order'

    name = fields.Char('Nombre',readonly=1)

    state = fields.Selection([('progress','En Progeso'),('done','Hecha')])

    customer_id = fields.Many2one('res.partner','Cliente')

    saleman_id = fields.Many2one('res.partner','Vendedor')

    date_done = fields.Datetime('Fecha de entrega')

    product_ids = fields.Many2many('product.product','Producto')

    total_sale = fields.Float('Total')

    sale_id = fields.Many2one('sale.order','Venta Interna')

    location_id = fields.Many2one('stock.location','Ubicacion')

    is_loan = fields.Boolean('Es Prestamo')

    @api.model
    def create(self, values):
        values['state'] = 'progress'
        values['name'] = self.env['ir.sequence'].next_by_code('mobile.sale.order')
        return super(ModileSaleOrder,self).create(values)
from odoo import fields, models, api

class CustomDiscountHistory(models.Model):

    _name = 'custom.discount.history'

    sale_id = fields.Many2one('sale.order', string="Pedido")

    customer_id = fields.Many2one('res.partner', string="Cliente")

    discount_amount = fields.Integer(string="Monto Descuento", compute="_compute_discount_amount")

    date_discount = fields.Datetime(string="Fecha del Descuento")

    discount_state = fields.Selection([('Por Cobrar','Por Cobrar'),('Cobrado','Cobrado')], string="Estado")

    def _compute_discount_amount(self):
        for item in self:
            sale_order = self.env['sale.order'].search([('id','=',item.sale_id.id)]) 
            total_discount_amount = 0
            if sale_order:
                if len(sale_order.order_line) > 0:
                    for line in sale_order.order_line:  
                        if line.product_id.categ_id.id == 7:
                            total_discount_amount += (-1 * line.product_id.lst_price)

            item.discount_amount = total_discount_amount

            
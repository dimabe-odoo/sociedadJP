from odoo import models, fields


class RefillTruckLine(models.Models):
    _name = 'refill.truck.line'

    config_id = fields.Many2one('refill.truck.config', auto_join=True)

    product_id = fields.Many2one('product.product', 'Producto')

    qty = fields.Integer('Cantidad')

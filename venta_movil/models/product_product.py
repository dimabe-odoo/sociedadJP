from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    supply_id = fields.Many2one('product.product',related='product_tmpl_id.supply_id', string='Envase')



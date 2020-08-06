from odoo import models, fields, api
class ProductProduct(models.Model):
    _inherit = 'product.product'
    supply_id = Many2one('product.product', string='Insumo')
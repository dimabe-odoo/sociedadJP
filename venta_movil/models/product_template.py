from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    supply = fields.Many2one('product.product')

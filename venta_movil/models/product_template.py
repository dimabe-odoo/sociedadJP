from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    supply_id = fields.Many2one('product.product')

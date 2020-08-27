from odoo import fields, models, api


class ModelName (models.Model):
    _inherit = 'purchase.order'

    have_purchase_without_supply = fields.Boolean('¿Tiene compra comodato?')



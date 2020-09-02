from odoo import fields, models, api


class PosSession (models.Model):
    _inherit = 'pos.session'

    supply_id = fields.Integer()

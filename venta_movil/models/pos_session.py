from odoo import fields, models, api


class PosSession (models.Model):
    _inherit = 'pos.session'
    _description = 'Description'

    name = fields.Char()

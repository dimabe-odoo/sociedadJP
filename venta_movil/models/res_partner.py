from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'
    jp_commune_id = fields.Many2one('jp.commune', string='Comuna')
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'
    jp_commune_id = fields.Many2one('jp.commune', string='Comuna')
    country_id = fields.Many2one('res.country', string='País', default=lambda self: self.env[
        'res.country'].search([('code', '=', 'CL')]))
    address_favorite_id = fields.Many2one(string='Direccion Favorita',comodel_name='res.partner')
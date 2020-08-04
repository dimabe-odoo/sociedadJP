from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'
    jp_commune_id = fields.Many2one('jp.commune', string='Comuna')
    country_id = fields.Many2one('res.country', string='País',default=_get_default_country)

    @api.model
    def _get_default_country(self):
        country = self.env['res.country'].search([('code', '=', 'CL')], limit=1)
        return country

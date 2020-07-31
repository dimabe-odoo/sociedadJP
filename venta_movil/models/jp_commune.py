from odoo import models, fields, api

class JpCommune(models.Model):
    _name = 'jp.commune'
    state_id = fields.Many2one('res.country.state')
    name = fields.Char(string='Comuna')

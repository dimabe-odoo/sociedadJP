from odoo import models, fields

class JpOrder(models.Model):
    _name = 'jp.order'
    client = fields.Many2one('res.user')
    employee = fields.Many2one('hr.employee')
    delivery_man = fields.Many2one('hr.employee')
    
from odoo import models, fields


class RefillTruckConfig(models.Model):
    _name = 'refill.truck.config'

    line_ids = fields.One2many('refill.truck.line', 'config_id')

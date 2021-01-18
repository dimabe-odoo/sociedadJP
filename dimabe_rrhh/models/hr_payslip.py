from odoo import models, fields


class HrPaySlip(models.Model):
    _inherit = 'hr.payslip'

    indicator_ids = fields.Many2one('custom.indicators')
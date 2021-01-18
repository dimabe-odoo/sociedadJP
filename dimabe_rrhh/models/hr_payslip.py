from odoo import models, fields


class HrPaySlip(models.Model):
    _inherit = 'hr.payslip'

    indicator_id = fields.Many2one('custom.indicators', string='Indicadores')

    def compute_sheet(self):
        raise models.ValidationError(self.indicator_id.mapped('data_ids').filtered(lambda a: a.type == '1' and not a.last_month).value)
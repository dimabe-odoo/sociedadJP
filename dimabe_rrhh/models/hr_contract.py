from odoo import models, fields


class HrContract(models.Model):
    _inherit = 'hr.contract'

    afp_id = fields.Many2one('custom.afp', 'AFP')

    isapre_id = fields.Many2one('custom.isapre', 'Isapre')

    apv_id = fields.Many2one('custom.data', domain=[('data_type_id', '=', 6)])
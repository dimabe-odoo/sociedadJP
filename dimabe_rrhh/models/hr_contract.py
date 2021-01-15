from odoo import models, fields


class HrContract(models.Model):
    _inherit = 'hr.contract'

    afp_id = fields.Many2one('custom.afp', 'AFP')

    isapre_id = fields.Many2one('custom.isapre', 'Isapre')

    apv_id = fields.Many2one('custom.data', domain=[('data_type_id', '=', 1)])

    currency_isapre_id = fields.Many2one('res.currency', 'Moneda', domain=[('id', 'in', (171, 173))])

    is_pensionary = fields.Boolean('Pensionado')

    type_pensionary = fields.Selection(
        [('old', 'Pensíon de Vejez'), ('disability', 'Pension de Invalidez'), ('survival', 'Pension de Sobreviviencia'),
         ('no', 'No Pensionado')]
        , default='no', string='Tipo de Pension')

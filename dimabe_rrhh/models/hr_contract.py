from odoo import models, fields


class HrContract(models.Model):
    _inherit = 'hr.contract'

    afp_id = fields.Many2one('custom.afp', 'AFP')

    isapre_id = fields.Many2one('custom.isapre', 'Isapre')

    frame_id = fields.Many2one('custom.data','Tramo',domain=[('data_type_id','=',6)])

    simple_charge = fields.Integer('Carga Simple')

    maternal_charge = fields.Integer('Carga Materna')

    disability_charge = fields.Integer('Carga Invalidez')

    apv_id = fields.Many2one('custom.data','APV', domain=[('data_type_id', '=', 1)])

    currency_isapre_id = fields.Many2one('res.currency', 'Moneda', domain=[('id', 'in', (171, 173))])

    is_pensionary = fields.Boolean('Pensionado')

    type_pensionary = fields.Selection(
        [('old', 'Pensíon de Vejez'), ('disability', 'Pension de Invalidez'), ('survival', 'Pension de Sobreviviencia'),
         ('no', 'No Pensionado')]
        , default='no', string='Tipo de Pension')

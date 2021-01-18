from odoo import models, fields


class HrContract(models.Model):
    _inherit = 'hr.contract'

    afp_id = fields.Many2one('custom.afp', 'AFP')

    apv_id = fields.Many2one('custom.data', 'Insticion APV', domain=[('data_type_id', '=', 1)])

    is_fonasa = fields.Boolean('Es Fonasa')

    isapre_id = fields.Many2one('custom.isapre', 'Isapre')

    frame_id = fields.Many2one('custom.data', 'Tramo', domain=[('data_type_id', '=', 6)])

    simple_charge = fields.Integer('Carga Simple')

    maternal_charge = fields.Integer('Carga Materna')

    disability_charge = fields.Integer('Carga Invalidez')

    isapre_agreed_quotes_uf = fields.Float('Cotizacion Pactada')

    fun_number = fields.Integer('Numero FUN')

    own_account_isapre = fields.Boolean('Cuenta propia isapre')

    supplementary_insurance_id = fields.Many2one('custom.data',string='Seguro Complementario', domain=['data_type_id', '=', 4])

    not_afp = fields.Boolean('No Cotiza AFP')

    not_afp_sis = fields.Boolean('No Cotiza AFP SIS')

    have_saving_ccaf = fields.Boolean('Tiene Ahorro CCAF')

    saving_ccaf = fields.Float('Ahorro CCAF')

    currency_supplementary_insurance_id = fields.Many2one('res.currency', 'Moneda', domain=[('id', 'in', (45, 173))])

    supplementary_insurance_agreed_quotes_uf = fields.Float('Cotizacion Pactada')

    currency_isapre_id = fields.Many2one('res.currency', 'Moneda', domain=[('id', 'in', (45, 173))])

    is_pensionary = fields.Boolean('Pensionado')

    type_pensionary = fields.Selection(
        [('old', 'Pensíon de Vejez'), ('disability', 'Pension de Invalidez'), ('survival', 'Pension de Sobreviviencia'),
         ('no', 'No Pensionado')]
        , default='no', string='Tipo de Pension')

from odoo import fields, models, api


class StockLocation(models.Model):
    _inherit = 'stock.location'

    loan_location = fields.Boolean('¿Es ubicacion de prestamo?')

    is_truck = fields.Boolean('¿Es Camion?')

    user_id = fields.Many2one('res.users')

    @api.onchange('is_truck')
    def onchange_istruck(self):
        if self.is_truck:
            res = {
                'invisible': {
                    'user_id': {
                        0
                    }
                }
            }
        else:
            res = {
                'invisible': {
                    'user_id': {
                        1
                    }
                }
            }
        return res

        amount = 0
if worked_days.WORK100.number_of_days == 0:
    result = 0
else:
    if inputs.HEX50:
        amount = inputs.HEX50.amount
DEVENGABLE = round(contract.wage + contract.otros_imp + amount)
if worked_days.WORK100.number_of_days == 0:
    result = 0
else:
    GRATI = round(DEVENGABLE * 25 / 100)
    if GRATI > (4.75 * payslip.indicadores_id.sueldo_minimo / 12):
        GRATI = round(4.75 * payslip.indicadores_id.sueldo_minimo / 12)
    else:
        GRATI = GRATI
if worked_days.WORK100.number_of_days == 0:
    result = 0
else:
    if TOTIM >= round(payslip.indicadores_id.tope_imponible_seguro_cesantia * payslip.indicadores_id.uf):
        totimpo = round(payslip.indicadores_id.tope_imponible_seguro_cesantia * payslip.indicadores_id.uf)
    elif TOTIM == 0:
        totimpo = round(DEVENGABLE + GRATI)
    else:
        totimpo = TOTIM
    if contract.pension is True:
        result = 0
    elif contract.type_id.name == 'Sueldo Empresarial':
        result = 0
    elif contract.type_id.name == 'Plazo Indefinido':
        result = round(totimpo * payslip.indicadores_id.contrato_plazo_indefinido_empleador / 100)
    elif contract.type_id.name == 'Indefinido 11 anos o mas':
        result = round(TOTIM * payslip.indicadores_id.contrato_plazo_indefinido_empleador_otro / 100)
    elif contract.type_id.name == 'Plazo Fijo':
        result = round(totimpo * payslip.indicadores_id.contrato_plazo_fijo_empleador / 100)
    else:
        result = 0



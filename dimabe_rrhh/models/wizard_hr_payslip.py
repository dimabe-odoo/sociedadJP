from odoo import api, fields, models
import xlsxwriter
from datetime import datetime
import base64
from collections import Counter

class WizardHrPayslip(models.TransientModel):
    _name = "wizard.hr.payslip"
    _description = 'XLSX Report'

    indicator_id = fields.Many2one('custom.indicators', string="Indicador")

    company_id = fields.Many2one('res.partner', domain=lambda self: [
        ('id', 'in', self.env['hr.employee'].sudo().search([('active', '=', True)]).mapped('address_id').mapped('id'))])

    #month = fields.Selection(
    #    [('Enero', 'Enero'), ('Febrero', 'Febrero'), ('Marzo', 'Marzo'), ('Abril', 'Abril'), ('Mayo', 'Mayo'),
    #     ('Junio', 'Junio'), ('Julio', 'Julio'),
    #     ('Agosto', 'Agosto'), ('Septiembre', 'Septiembre'), ('Octubre', 'Octubre'), ('Noviembre', 'Noviembre'),
    #     ('Diciembre', 'Diciembre'), ], string="Mes")

    #years = fields.Integer(string="Años", default=int(datetime.now().year))

    def print_report_xlsx(self):
        file_name = 'temp'
        workbook = xlsxwriter.Workbook(file_name)
        worksheet = workbook.add_worksheet(self.company_id.name)
        number_format=workbook.add_format({'num_format': '#,###'})
        indicators = self.env['custom.indicators'].sudo().search([('id', '=', f'{self.indicator_id.id}')])
        if not indicators:
            raise models.ValidationError(f'No existen datos del mes de {self.indicator_id.name}')
        if indicators.state != 'done':
            raise models.ValidationError(
                f'Los indicadores provicionales del mes de {indicators.name} no se encuentran validados')
        row = 13
        col = 0

        #payslips = self.env['hr.payslip'].sudo().search(
        #    [('indicator_id', '=', indicators.id), ('state', 'in', ['done', 'draft']),('employee_id.address_id.id','=',self.company_id.id), ('name', 'not like', 'Devolución:')])

        payslips = self.env['hr.payslip'].sudo().search(
            [('indicator_id', '=', indicators.id), ('state', 'in', ['done', 'draft'])])

        totals = self.env['hr.payslip.line'].sudo().search([('slip_id', 'in', payslips.mapped('id'))]).filtered(
            lambda a: a.total > 0)

        totals_result = []
        payslips = totals.mapped('slip_id')
        bold_format = workbook.add_format({'bold': True})
        worksheet.write(0, 0, self.company_id.name,bold_format)
        # GIRO worksheet.write(1,0, 'PROCESO Y COMERCIALIZACION DE NUECES', bold_format)
        worksheet.write(2,0, self.company_id.street, bold_format)
        worksheet.write(3,0, self.company_id.city, bold_format)
        worksheet.write(4,0, self.company_id.country_id.name, bold_format)
        worksheet.write(5,0, self.company_id.invoice_rut, bold_format)
        worksheet.write(6,0, 'Fecha Informe : '+datetime.today().strftime('%d-%m-%Y'), bold_format)
        worksheet.write(7,0, self.month, bold_format)
        worksheet.write(8,0, 'Fichas : Todas', bold_format)
        worksheet.write(9,0, 'Área de Negocio : Todas las Áreas de Negocios', bold_format)
        worksheet.write(10,0, 'Centro de Costo : Todos los Centros de Costos', bold_format)
        worksheet.write(11,0, 'Total Trabajadores : '+ str(len(payslips)), bold_format)
        for pay in payslips:
            rules = self.env['hr.salary.rule'].sudo().search([('id', 'in', totals.mapped('salary_rule_id').mapped('id'))],
                                                      order='order_number')
            col = 0

            worksheet.write(row, col, pay.employee_id.display_name)
            worksheet.write(12, 0, 'Nombre', bold_format)
            long_name = max(payslips.mapped('employee_id').mapped('display_name'), key=len)
            worksheet.set_column(row, col, len(long_name))
            col += 1
            worksheet.write(12, 1, 'Rut', bold_format)
            worksheet.write(row, col, pay.employee_id.identification_id)
            long_rut = max(payslips.mapped('employee_id').mapped('identification_id'), key=len)
            worksheet.set_column(row, col, len(long_rut))
            col += 1
            worksheet.write(12, 2, 'N° Centro de Costo', bold_format)
            if pay.account_analytic_id:
                worksheet.write(row, col, pay.account_analytic_id.code)
            elif pay.contract_id.department_id.analytic_account_id:
                worksheet.write(row, col, pay.contract_id.department_id.analytic_account_id.code)
            else:
                worksheet.write(row, col, '')
            long_const = max(
                payslips.mapped('contract_id').mapped('department_id').mapped('analytic_account_id').mapped('name'),
                key=len)
            worksheet.set_column(row, col, len(long_const))
            col += 1
            worksheet.write(12, 3, 'Centro de Costo:', bold_format)
            if pay.account_analytic_id:
                worksheet.write(row, col, pay.account_analytic_id.name)
            elif pay.contract_id.department_id.analytic_account_id:
                worksheet.write(row, col, pay.contract_id.department_id.analytic_account_id.name)
            else:
                worksheet.write(row, col, '')
            long_const = max(
                payslips.mapped('contract_id').mapped('department_id').mapped('analytic_account_id').mapped('name'),
                key=len)
            worksheet.set_column(row, col, len(long_const))
            col += 1
            worksheet.write(12, 4, 'Dias Trabajados:', bold_format)
            worksheet.write(row, col, self.get_worked_days(pay))
            col += 1
            worksheet.write(12, col, 'Cant. Horas Extras', bold_format)
            worksheet.write(row, col, self.get_qty_extra_hours(payslip=pay))
            totals_result.append({col : self.get_qty_extra_hours(payslip=pay)})
            col += 1
            for rule in rules:
                if not rule.show_in_book:
                    continue
                if not totals.filtered(lambda a: a.salary_rule_id.id == rule.id):
                    continue
                if rule.code == 'HEX50':
                    worksheet.write(12, col, 'Valor Horas Extras', bold_format)
                    total_amount = self.env["hr.payslip.line"].sudo().search(
                        [("slip_id", "=", pay.id), ("salary_rule_id", "=", rule.id)]).total
                    worksheet.write(row, col, total_amount,number_format)
                    totals_result.append({col : total_amount})
                elif rule.code == 'HEXDE':
                    worksheet.write(12, col, 'Cant. Horas Descuentos', bold_format)
                    worksheet.write(row, col, self.get_qty_discount_hours(payslip=pay))
                    totals_result.append({col : self.get_qty_discount_hours(payslip=pay)})
                    col += 1
                    worksheet.write(12, col, 'Monto Horas Descuentos', bold_format)
                    total_amount = self.env["hr.payslip.line"].sudo().search(
                        [("slip_id", "=", pay.id), ("salary_rule_id", "=", rule.id)]).total
                    worksheet.write(row, col,total_amount,number_format)
                    totals_result.append({col : total_amount})
                else:
                    total_amount = self.env["hr.payslip.line"].sudo().search(
                        [("slip_id", "=", pay.id), ("salary_rule_id", "=", rule.id)]).total
                    worksheet.write(12, col, rule.name, bold_format)
                    worksheet.write(row, col,total_amount,number_format)
                    totals_result.append({col : total_amount})
                col += 1
            col = 0
            row += 1
        counter = Counter()
        for item in totals_result:
            counter.update(item)
        total_dict = dict(counter)
        worksheet.write(row, 0, 'Totales',bold_format)
        number_bold_format = workbook.add_format({'num_format': '#,###', 'bold': True})
        for k in total_dict:
            worksheet.write(row, k,total_dict[k],number_bold_format)
        col = 0
        row += 1
        workbook.close()
        with open(file_name, "rb") as file:
            file_base64 = base64.b64encode(file.read())

        file_name = 'Libro de Remuneraciones {}'.format(indicators.name)
        attachment_id = self.env['ir.attachment'].sudo().create({
            'name': file_name,
            'datas_fname': file_name,
            'datas': file_base64
        })
        action = {
            'type': 'ir.actions.act_url',
            'url': '/web/content/{}?download=true'.format(attachment_id.id, ),
            'target': 'current',
        }
        return action

    @api.model
    def get_workd_days(self, payslip):
        worked_days = 0
        if payslip:
            for line in payslip.worked_days_line_ids:
                if line.code == 'WORK100':
                    worked_days = line.number_of_days
        return worked_days

    @api.model
    def get_qty_extra_hours(self, payslip):
        worked_days = 0
        if payslip:
            for line in payslip.input_line_ids:
                if line.code == 'HEX50':
                    worked_days = line.amount
        return worked_days

    @api.model
    def get_qty_discount_hours(self, payslip):
        worked_days = 0
        if payslip:
            for line in payslip.input_line_ids:
                if line.code == 'HEXDE':
                    worked_days = line.amount
        return worked_days
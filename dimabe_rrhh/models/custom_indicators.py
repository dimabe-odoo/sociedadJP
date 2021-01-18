from odoo import fields, models, api
import requests
from bs4 import BeautifulSoup
from odoo.addons import decimal_precision as dp
from datetime import datetime


class CustomIndicators(models.Model):
    _name = 'custom.indicators'

    name = fields.Char('Nombre')

    data_ids = fields.Many2many('custom.indicators.data')
    month = fields.Selection(
        [('jan', 'Enero'), ('feb', 'Febrero'), ('mar', 'Marzo'), ('apr', 'Abril'), ('may', 'Mayo'), ('jun', 'Junio'),
         ('jul', 'Julio'), ('aug', 'Agosto'), ('sep', 'Septiembre'), ('oct', 'Octubre'), ('nov', 'Noviembre'),
         ('dec', 'Diciembre')])

    year = fields.Float('Año', default=datetime.now().strftime('%Y'), digits=dp.get_precision('Year'))

    @api.model
    def create(self, vals):
        vals['name'] = f'{self.get_month(vals["month"])} {vals["year"]}'
        return super(CustomIndicators, self).create(vals)

    def get_data(self):
        indicators = self.get_data_from_url()
        for indicator in indicators:
            if isinstance(indicator, dict):
                for value in indicator['data']:
                    ind = self.env['custom.data'].create({
                        'name': value['title'].capitalize(),
                        'value': value['value'],
                        'data_type_id': 5
                    })
                    self.write({
                        'data_ids': [(4, ind.id)]
                    })
            else:
                for data in indicator:
                    for value in data['data']:
                        ind = self.env['custom.data'].create({
                            'name': f"{data['title'].capitalize()} {value['title'].lower()}",
                            'value': value['data'],
                            'data_type_id': 5
                        })
                        self.write({
                            'data_ids': [(4, ind.id)]
                        })

    def clear_string(self, cad):
        cad = cad.replace(".", '').replace("$", '').replace(" ", '')
        cad = cad.replace("Renta", '').replace("<", '').replace(">", '')
        cad = cad.replace("=", '').replace("R", '').replace("I", '').replace("%", '')
        cad = cad.replace(",", '.')
        cad = cad.replace("1ff8", "")
        return cad

    def get_data_from_url(self):
        link = 'https://www.previred.com/web/previred/indicadores-previsionales'
        data = requests.get(link)
        soup = BeautifulSoup(data.text, 'html.parser')
        tables = soup.find_all('table')
        indicators = []
        values = []
        for table in tables:
            if table == tables[0]:
                uf_value = self.get_table_type_1(table)
                for item in uf_value:
                    raise models.ValidationError(type(item))
            elif table == tables[1]:
                table_data = self.get_utm_uta(table)
                indicators.append(table_data)
            elif table == tables[2]:
                table_data = self.get_table_type_1(table)
                indicators.append(table_data)
            elif table == tables[3]:
                table_data = self.get_table_type_1(table)
                indicators.append(table_data)
            elif table == tables[4]:
                table_data = self.get_table_type_1(table)
                indicators.append(table_data)
            elif table == tables[5]:
                table_data = self.get_table_type_1(table)
                indicators.append(table_data)
            elif table == tables[6]:
                data = self.get_safe(table)
                table_data ={
                    'title':'Seguro de Cesantia (AFC)',
                    'data': data
                }
                indicators.append(table_data)
            elif table == tables[7]:
                data = self.get_afp_data(table)
                table_data = {
                    'title': 'Tasa Cotizacion Obligatoria AFP',
                    'data': data
                }
                indicators.append(table_data)

        return indicators


    def get_afp_data(self,table):
        data = []
        afp_rate_capital = {
            'title': 'Tasa Afp Capital',
            'value':self.clear_string(table.select("strong")[8].get_text())
        }
        data.append(afp_rate_capital)
        sis_rate_capital = {
            'title': 'Tasa SIS Capital',
            'value':self.clear_string(table.select("strong")[9].get_text())
        }
        data.append(sis_rate_capital)

        afp_rate_cuprum = {
            'title':'Tasa Afp Cuprum',
            'value':self.clear_string(
            table.select("strong")[11].get_text().replace(" ", '').replace("%", '').replace("1ff8", ''))
        }
        data.append(afp_rate_cuprum)
        sis_rate_cuprum = {
            'title':'Tasa SIS Cuprum',
            'value':self.clear_string(table.select("strong")[12].get_text())
        }
        data.append(sis_rate_cuprum)

        afp_rate_habitat = {
            'title': 'Tasa Afp Habitat',
            'value':self.clear_string(table.select("strong")[14].get_text())
        }
        data.append(afp_rate_habitat)
        sis_rate_habitad = {
            'title': 'Tasa SIS Habitat',
            'value': self.clear_string(table.select("strong")[15].get_text())
        }
        data.append(sis_rate_habitad)

        afp_rate_planvital = {
            'title': 'Tasa Afp PlanVital',
            'value': self.clear_string(table.select("strong")[17].get_text())
        }
        data.append(afp_rate_planvital)
        sis_rate_planvital = {
            'title': 'Tasa SIS PlanVital',
            'value': self.clear_string(table.select("strong")[18].get_text())
        }
        data.append(sis_rate_planvital)

        afp_rate_provida = {
            'title': 'Tasa Afp Provida',
            'value': self.clear_string(
            table.select("strong")[20].get_text().replace(" ", '').replace("%", '').replace("1ff8", ''))
        }
        data.append(afp_rate_provida)
        sis_rate_provida = {
            'title': 'Tasa SIS Provida',
            'value': self.clear_string(table.select("strong")[21].get_text())
        }
        data.append(sis_rate_provida)

        afp_rate_modelo = {
            'title': 'Tasa Afp Modelo',
            'value': self.clear_string(table.select("strong")[23].get_text())
        }
        data.append(afp_rate_modelo)
        sis_rate_modelo = {
            'title': 'Tasa SIS Modelo',
            'value': self.clear_string(table.select("strong")[24].get_text())
        }
        data.append(sis_rate_modelo)


        afp_rate_uno = {
            'title': 'Tasa Afp Uno',
            'value': self.clear_string(table.select("strong")[26].get_text())
        }
        data.append(afp_rate_uno)
        sis_rate_uno = {
            'title': 'Tasa SIS Uno',
            'value': self.clear_string(table.select("strong")[27].get_text())
        }
        data.append(sis_rate_uno)

        return data

    def get_safe(self, table):
        data = []
        contract_undefined_employer = {'title': 'Contracto Plazo Indefinido Empleador',
                                       'value': self.clear_string(table.select("strong")[5].get_text())}
        data.append(contract_undefined_employer)
        contract_undefined_employee = {'title': 'Contracto Plazo Indefinido Trabajador',
                                       'value': self.clear_string(table.select("strong")[6].get_text())}
        data.append(contract_undefined_employee)
        contract_fixed_term_employer = {'title': 'Contracto Plazo Fijo Empleador',
                                        'value': self.clear_string(table.select("strong")[7].get_text())}
        data.append(contract_fixed_term_employer)
        contract_undefined_employer_other = {'title': 'Contacto Plazo Empleador Otro',
                                             'value': self.clear_string(table.select("strong")[9].get_text())}
        data.append(contract_undefined_employer_other)
        return data

    def get_utm_uta(self, table):
        title_principal = f"{table.find_all('td')[0].get_text()} {table.find_all('td')[3].get_text()}"
        list = []
        title = ''
        value = 0.0
        for td in table.find_all('td'):
            if td == table.find_all('td')[0] or td == table.find_all('td')[3]:
                continue
            else:
                if self.clear_string(td.get_text()).isdigit():
                    value = float(self.clear_string(td.get_text()))
                else:
                    title = self.clear_string(td.get_text())
                if value != 0.0:
                    list.append({
                        'title': title,
                        'value': value
                    })
        list[0]['title'] = 'UTM'
        return {'title': title_principal, 'data': list}

    def get_table_type_1(self, table):
        values = []
        uf = []
        title = ''
        value = 0.0
        subtitle = ''
        for td in table.find_all('td'):
            if td == table.select('td')[0]:
                title = td.get_text()
            else:
                if '$' in td.get_text():
                    value = float(self.clear_string(td.get_text()))
                else:
                    subtitle = td.get_text()
                if value == 0.0:
                    continue
                values.append({
                    'title': subtitle,
                    'data': value
                })
                value = 0.0
                subtitle = ''
        uf.append({
            'title': title,
            'data': values
        })
        return uf

    def get_month(self, month):
        if 'jan' == month:
            return 'Enero'
        elif 'feb' == month:
            return 'Febrero'
        elif 'mar' == month:
            return 'Marzo'
        elif 'apr' == month:
            return 'Abril'
        elif 'may' == month:
            return 'Mayo'
        elif 'jun' == month:
            return 'Junio'
        elif 'jul' == month:
            return 'Julio'
        elif 'aug' == month:
            return 'Agosto'
        elif 'sep' == month:
            return 'Septiembre'
        elif 'oct' == month:
            return 'Octubre'
        elif 'nov' == month:
            return 'Noviembre'
        elif 'dec' == month:
            return 'Diciembre'

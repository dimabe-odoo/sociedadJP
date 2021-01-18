from odoo import fields, models, api
import requests
from bs4 import BeautifulSoup


class CustomIndicators(models.Model):
    _name = 'custom.indicators'

    name = fields.Char('Nombre')

    data_ids = fields.Many2many('custom.data')

    month = fields.Selection(
        [('jan', 'Enero'), ('feb', 'Febrero'), ('mar', 'Marzo'), ('apr', 'Abril'), ('may', 'Mayo'), ('jun', 'Junio'),
         ('jul', 'Julio'), ('aug', 'Agosto'), ('sep', 'Septiembre'), ('oct', 'Octubre'), ('nov', 'Noviembre'),
         ('dec', 'Diciembre')])

    year = fields.Float()

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
                indicators.append(uf_value)
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
        return indicators

    def get_safe(self, table):
        for td in table.find_all('td'):
            print(td.get_text())

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

from odoo import fields, models, api
import requests
from bs4 import BeautifulSoup


class CustomIndicators(models.Model):
    _name = 'custom.indicators'

    name = fields.Char('Nombre')

    data_ids = fields.Many2many('custom.data')

    def get_data(self):
        indicators = self.get_data_from_url()
        for indicator in indicators:
            for d in indicator['data']:
                self.env['custom.data'].create({
                    'name': f"{indicator['title']} {d['title']}",
                    'value': d['data'],
                    'data_type_id': 5
                })

    def clear_string(self,cad):
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
        title = ''
        for table in tables:
            value = 0.0
            subtitle = ''
            if table == tables[0]:
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
                indicators.append({
                    'title': title,
                    'data': values
                })

        return indicators

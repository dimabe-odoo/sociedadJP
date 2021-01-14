from odoo import fields, models, api
import requests
import bs4 as bs4


class CustomIndicators(models.Model):
    _name = 'custom.indicators'

    name = fields.Char('Nombre')

    data_ids = fields.Many2many('custom.data')

    def get_data(self):
        indicators = self.get_data_from_url()
        for indi in indicators:
            for ind in indi['data']:
                if ind['data'] != 0 or ind['data'] != '':
                    self.env['custom.data'].create({
                        'name': f"{indi['title']} {ind['title']}",
                        'value': f"{ind['data']}"
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
        soup = bs4.BeautifulSoup(data.text)
        tables = soup.find_all('table')
        indicators = []
        values = []
        title = ''
        subtitle = ''
        value = ''
        for table in tables:
            if table == tables[0]:
                if table == tables[0]:
                    for str in table.find_all('td'):
                        if str == table.select('td')[0]:
                            title = str.get_text()
                        else:
                            if '$' in str.get_text():
                                value = float(self.clear_string(str.get_text()))
                            else:
                                subtitle = str.get_text()
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

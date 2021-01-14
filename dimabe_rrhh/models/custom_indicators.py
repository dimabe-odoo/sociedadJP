from odoo import fields, models, api
import requests
import bs4 as bs4


class CustomIndicators(models.Model):
    _name = 'custom.indicators'

    name = fields.Char('Nombre')

    data_ids = fields.Many2many('custom.data')

    def get_data(self):
        indicators = self.get_data_from_url()
        raise models.ValidationError(list(indicators))

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
        for table in tables:
            if table == tables[0]:
                for str in table.select('strong'):
                    if str == table.select('strong')[0]:
                        title = str.get_text()
                    else:
                        values.append(str.get_text())
                indicators.append({
                    'title': title,
                    'data': data
                })

        return indicators

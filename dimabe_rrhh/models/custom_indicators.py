from odoo import fields, models, api
import requests
import bs4 as bs4


class CustomIndicators(models.Model):
    _name = 'custom.indicators'

    name = fields.Char('Nombre')

    data_ids = fields.Many2many('custom.data')

    def get_data(self):
        link = 'https://www.previred.com/web/previred/indicadores-previsionales'
        data = requests.get(link)
        soup = bs4.BeautifulSoup(data.text)
        tables = soup.find_all('table')
        uf = tables[0].select("strong")[1].get_text()
        uf_last = tables[0].select("strong")[2].get_text()
        indicadors_ids = []
        uf_data = self.env['custom.data'].create({
            'name': 'Valor de Mes',
            'value': float(self.clear_string(uf)),
            'data_type_id': 1
        })
        indicadors_ids.append(uf_data.id)
        uf_last_data = self.env['custom.data'].create({
            'name':"Valor Mes Anterior",
            'value': float(self.clear_string(uf_last)),
            'data_type_id' : 1
        })
        indicadors_ids.append(uf_last_data.id)




    def clear_string(self, cad):
        cad = cad.replace(".", '').replace("$", '').replace(" ", '')
        cad = cad.replace("Renta", '').replace("<", '').replace(">", '')
        cad = cad.replace("=", '').replace("R", '').replace("I", '').replace("%", '')
        cad = cad.replace(",", '.')
        cad = cad.replace("1ff8", "")
        return cad

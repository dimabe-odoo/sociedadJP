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
        uf = self.env['custom.data'].sudo().create({
            'name':tables[0].select("strong")[0].get_text(),
            'value':float(tables[0].select("strong")[1].get_text().replace('$ ','').replace('.','').replace(',',''))
        })
        self.write({
            'data_ids':[(4,uf.id)]
        })
        raise models.ValidationError(tables[0].select("strong")[1].get_text())

    def clear_string(self,cad):
        cad = cad.replace(".", '').replace("$", '').replace(" ", '')
        cad = cad.replace("Renta", '').replace("<", '').replace(">", '')
        cad = cad.replace("=", '').replace("R", '').replace("I", '').replace("%", '')
        cad = cad.replace(",", '.')
        cad = cad.replace("1ff8", "")
        return cad
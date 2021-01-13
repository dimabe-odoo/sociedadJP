from odoo import fields, models, api
import requests
import bs4 as bs4

class CustomIndicators(models.Model):
    _name = 'custom.indicators'

    name = fields.Char('Nombre')

    def get_data(self):
        link = 'https://www.previred.com/web/previred/indicadores-previsionales'
        data = requests.get(link)
        raise models.ValidationError(bs4.BeautifulSoup(data.text))
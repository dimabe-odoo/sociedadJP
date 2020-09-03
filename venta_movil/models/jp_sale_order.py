from odoo import fields, models, api


class JpSaleOrder(models.Model):
    _name = 'jp.sale.order'

    name = fields.Char('Nombre')

    

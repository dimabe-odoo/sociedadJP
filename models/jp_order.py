from odoo import models, fields, api

class JpOrder(models.Model):
    _name = 'jp.order' 

    employee_id = fields.Many2one(comodel_name='hr.employee', string='Vendedor')
    delivery_man_id = fields.Many2one(comodel_name='hr.employee', string='Repartidor')
    client_id = fields.Many2one(comodel_name='res.partner', string='Cliente')
    warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string='Camión')


     
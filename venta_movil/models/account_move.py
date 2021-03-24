from odoo import models
import datetime

class AccountMove(models.Model):
    _inherit ='account.move'

    def create(self, values):
        for value in values:
            if value['invoice_origin']:
                sale_order = self.env['sale.order'].search([('name','=',value['invoice_origin'])])
                if sale_order:
                    discount_history = self.env['custom.discount.history'].create({
                        'sale_id': sale_order.id,
                        'customer_id': value['partner_id'],
                        'date_discount': datetime.datetime.now()
                    })
        return super(AccountMove, self).create(values)



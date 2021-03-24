from odoo import models
import datetime

class AccountMove(models.Model):
    _inherit ='account.move'

    #def create(self, values):
    #    for value in values:
    #        if value['invoice_origin']:
    #            sale_order = self.env['sale.order'].search([('name','=',value['invoice_origin'])])
    #            if sale_order:
    #                discount_history = self.env['custom.discount.history'].create({
    #                    'sale_id': sale_order.id,
    #                    'customer_id': value['partner_id'],
    #                    'date_discount': datetime.datetime.now()
    #                })
    #    return super(AccountMove, self).create(values)
    
    def write(self, values):
        if 'invoice_payment_state' in values.keys():
            raise models.ValidationError(values['invoice_payment_state'])
            if values['invoice_payment_state'] == 'paid':
                sale_order = self.env['sale.order'].search([('name','=',values['invoice_origin'])])
                if sale_order:
                    discount_history = self.env['custom.discount.history'].create({
                        'sale_id': sale_order.id,
                        'customer_id': values['partner_id'],
                        'date_discount': datetime.datetime.now()
                })
        raise models.ValidationError('Not')
        return super(AccountMove, self).write(values)



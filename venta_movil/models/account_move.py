from odoo import models
import datetime

class AccountMove(models.Model):
    _inherit ='account.move'

    def write(self, values):
        if 'state' in values.keys():
            if values['state'] == 'posted':
                if values['invoice_origin']:
                    sale_order = self.env['sale.order'].search([('name','=',values['invoice_origin'])])

        if sale_order:
            if sale_order.id not in self.env['custom.discount.history'].mapped('sale_id'):
                discount_history = self.env['custom.discount.history'].create({
                    'sale_id': sale_order.id,
                    'customer_id': values['partner_id'],
                    'date_discount': datetime.datetime.now(),
                    'discount_state': 'Por Cobrar'
        })
        return super(AccountMove, self).write(values)






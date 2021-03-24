from odoo import models

class AccountMove(models.Model):
    _inherit ='account.move'

    def create(self, values):
        raise models.ValidationError(values.keys())
        discount_history = self.env['custom.discount.history'].create({
            'sale_id': values['sale_id'],
            'customer_id': values['partner_id'],
            'date_discount': self.datetime.now()
        })
        return super(AccountMove, self).create(values)
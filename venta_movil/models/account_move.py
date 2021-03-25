from odoo import models
import datetime

class AccountMove(models.Model):
    _inherit ='account.move'

    def _compute_amount(self):
        ids = ''
        for item in self:
            ids += item.id + ' '
        raise models.ValidationError(ids)
        #sale_order = self.env['sale.order'].search([('id','=',self.)])

        #if sale_order:
        #    discount_history = self.env['custom.discount.history'].create({
        #        'sale_id': sale_order.id,
        #        'customer_id': values['partner_id'],
        #        'date_discount': datetime.datetime.now()
        #})
        return super(AccountMove, self)._compute_amount()






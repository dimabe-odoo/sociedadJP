from odoo import models
import datetime


class AccountMove(models.Model):
    _inherit = 'account.move'

    def write(self, values):
        if 'state' in values.keys():
            if values['state'] == 'posted':
                if self.invoice_line_ids.mapped('sale_line_ids'):
                    sale_order = self.env['sale.order'].search(
                        [('id', '=', self.invoice_line_ids[0].sale_line_ids[0].order_id.id)])
                    if sale_order:
                        have_discount = False

                        for item in sale_order.order_line:
                            if item.product_id.categ_id.id == 7:
                                have_discount = True

                        if have_discount:
                            if sale_order.id not in self.env['custom.discount.history'].search([]).mapped(
                                    'sale_id').mapped('id'):
                                self.env['custom.discount.history'].create({
                                    'sale_id': sale_order.id,
                                    'sale_origin': 'Venta',
                                    'customer_id': sale_order.partner_id.id,
                                    'date_discount': datetime.datetime.now(),
                                    'discount_state': 'Por Cobrar',
                                    'warehouse_id': sale_order.warehouse_id.id
                                })
        return super(AccountMove, self).write(values)

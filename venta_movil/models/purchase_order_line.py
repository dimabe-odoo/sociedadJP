from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    purchase_without_supply = fields.Integer('Compra comodato')

    coupon_ids = fields.Many2many('custom.discount.history', string='Cupones')

    @api.onchange('purchase_without_supply')
    def onchange_purchase_without_supply(self):
        if self.product_qty < self.purchase_without_supply:
            raise models.ValidationError(
                'La cantidad de de compra comodato no puede ser mayor a la cantidad solicitidad')

    def write(self,values):
        if 'product_qty' in values.keys():
            diff = self.product_qty - values['product_qty']
            if diff >= 0:
                index = 0
                for coupon in self.coupon_ids:
                    if index > values['product_qty']:
                        break
                    coupon.write({
                        'discount_state': 'Por Cobrar',
                    })
                    self.write({
                        'coupon_ids': [(3,coupon.id)]
                    })
                    index += 1
        return super(PurchaseOrderLine, self).write(values)

    def unlink(self):
        if self.coupon_ids:
            self.coupon_ids.write({
                'discount_state': 'Por Cobrar'
            })
        return super(PurchaseOrderLine, self).unlink()
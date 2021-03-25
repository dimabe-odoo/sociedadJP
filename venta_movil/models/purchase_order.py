from odoo import fields, models, api


class PurchaseOrder (models.Model):
    _inherit = 'purchase.order'

    have_purchase_without_supply = fields.Boolean('¿Tiene compra comodato?')

    def add_discount_history(self):
        discount_history = self.env['custom.discount.history'].search([('discount_state', '=', 'Por Cobrar')])

        if (len(discount_history) > 0):
            discount_types = self.env['product.template'].search([('categ_id','=',7)])
            discount_counts = []
            for t in discount_types:
                discount_counts.append({
                        'id': t['id'],
                        'name': t['name'],
                        'price': t['list_price'],
                        'count': 0,
                        'uom': t['uom_po_id']['id']
                    })
            for item in discount_history:
                for line in discount_history.sale_id.order_line:
                    for d in discount_counts:
                        if line.product_id.name in d.name:
                            d['count'] += line.product_uom_qty

            for line in discount_counts:
                if line.count > 0:
                    self.order_line.create({
                        'product_template_id': line['id'],
                        'name': line['name'],
                        'product_qty': line['count'],
                        'price_unit': line['price'],
                        'product_uom': line['uom']
                    })

        else:
            raise models.ValidationError('No Posee Descuentos por Cobrar')




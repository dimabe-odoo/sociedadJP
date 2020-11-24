from odoo import fields, models, api
import datetime


class MobileSaleOrder(models.Model):
    _name = 'mobile.sale.order'

    name = fields.Char('Nombre', readonly=1)

    state = fields.Selection(
        [('cancel', 'Cancelado'), ('draft', 'Borrador'), ('confirm', 'Confirmado'), ('onroute', 'En Ruta'),
         ('done', 'Hecha')], default='draft',string='Estado')

    customer_id = fields.Many2one('res.partner', 'Cliente', required=True)

    address_id = fields.Many2one('res.partner', 'Direccion de envio')

    address_ids = fields.Many2many('res.partner', 'Direcciones del cliente', compute='compute_address_ids')

    price_list_id = fields.Many2one('product.pricelist', 'Lista de Precio del Cliente',
                                    related='customer_id.property_product_pricelist')

    saleman_id = fields.Many2one('hr.employee', 'Vendedor')

    date_done = fields.Datetime('Fecha de entrega')

    mobile_lines = fields.One2many('mobile.sale.line', 'mobile_id', 'Productos')

    total_sale = fields.Monetary('Total', compute='onchange_mobile_line')

    currency_id = fields.Many2one('res.currency', 'Moneda',
                                  default=lambda self: self.env['res.currency'].search([('name', '=', 'CLP')]))

    sale_id = fields.Many2one('sale.order', 'Venta Interna')

    paid = fields.Float('Pagado con')

    change = fields.Float('Vuelto')

    warehouse_id = fields.Many2one('stock.warehouse', 'Bodega')

    location_id = fields.Many2one('stock.location', 'Ubicacion', domain=[('is_truck', '=', True)])

    is_loan = fields.Boolean('Es Prestamo')

    @api.onchange('mobile_lines')
    def onchange_mobile_line(self):
        for item in self:
            total = []
            for line in item.mobile_lines:
                total.append(line.price * line.qty)
            item.total_sale = sum(total)

    @api.onchange('paid')
    def compute_change(self):
        for item in self:
            change = item.paid - item.total_sale
            if change > 0:
                item.change = change
            else:
                item.change = 0

    @api.onchange('customer_id')
    def onchange_address_id(self):
        res = {
            'domain': {
                'address_id': [('id', 'in', self.customer_id.child_ids.mapped('id'))]
            }
        }
        return res

    def button_confirm(self):
        self.write({
            'state': 'confirm'
        })

    @api.model
    def create(self, values):
        values['state'] = 'draft'
        values['name'] = self.env['ir.sequence'].next_by_code('mobile.sale.order')
        res = super(MobileSaleOrder, self).create(values)
        return res

    def button_dispatch(self):
        self.write({
            'state': 'onroute'
        })

    def cancel_order(self):
        self.write({
            'state':'cancel'
        })

    def make_done(self):
        loan = False
        if self.is_loan:
            loan = self.is_loan
        sale_odoo = self.env['sale.order'].create({
            'company_id': self.env.user.company_id.id,
            'currency_id': self.currency_id.id,
            'partner_id': self.customer_id.id,
            'picking_policy': 'direct',
            'origin': self.id,
            'with_delivery': True,
            'loan_supply': loan,
            'warehouse_id': self.warehouse_id.id,
            'pricelist_id': self.price_list_id.id
        })
        for line in self.mobile_lines:
            self.env['sale.order.line'].create({
                'name': sale_odoo.name,
                'product_id': line.product_id.id,
                'order_id': sale_odoo.id,
                'price_unit': line.price,
                'product_uom_qty': float(line.qty),
                'currency_id': line.currency_id.id
            })
        self.write({
            'state': 'done',
            'date_done': datetime.datetime.now(),
            'sale_id': sale_odoo.id
        })
        self.sale_id.action_confirm()
        self.mobile_lines.write({
            'state': 'done'
        })
        self.sale_id.picking_ids[0].write({
            'show_supply': True
        })
        for stock in self.sale_id.picking_ids[0].move_line_ids_without_package:
            stock.write({
                'qty_done': self.mobile_lines.filtered(lambda a: a.product_id.id == stock.product_id.id).qty
            })
        if self.is_loan:
            for move in self.sale_id.picking_ids[0].move_ids_without_package:
                move.write({
                    'loan_supply':self.mobile_lines.filtered(lambda a: a.product_id.id == move.product_id.id).loan_qty
                })
        self.sale_id.picking_ids[0].button_validate()
        dir(self.sale_id)
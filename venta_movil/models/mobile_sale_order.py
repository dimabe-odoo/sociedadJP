from odoo import fields, models, api
import datetime
from dateutil.relativedelta import *

class MobileSaleOrder(models.Model):
    _name = 'mobile.sale.order'

    name = fields.Char('Nombre', readonly=1)

    state = fields.Selection(
        [('cancel', 'Cancelado'), ('draft', 'Borrador'), ('confirm', 'Confirmado'), ('onroute', 'En Ruta'),
         ('done', 'Hecha')], default='draft', string='Estado')

    customer_id = fields.Many2one('res.partner', 'Cliente', required=True)

    address_id = fields.Many2one('res.partner', 'Otra Direccion de envio')

    address_ids = fields.Many2many(comodel_name='res.partner', string='Direcciones del cliente',
                                   rel='address_id.child_ids')

    price_list_id = fields.Many2one('product.pricelist', 'Lista de Precio del Cliente')

    seller_id = fields.Many2one('truck.session', 'Vendedor', domain=[('is_login', '=', True)])

    date_done = fields.Datetime('Fecha de entrega')

    mobile_lines = fields.One2many('mobile.sale.line', 'mobile_id', 'Productos')

    total_sale = fields.Monetary('Total',compute='onchange_mobile_line')

    currency_id = fields.Many2one('res.currency', 'Moneda',
                                  default=lambda self: self.env['res.currency'].search([('name', '=', 'CLP')]))

    sale_id = fields.Many2one('sale.order', 'Venta Interna')

    paid = fields.Float('Pagado con')

    confirm_date = fields.Datetime('Fecha Confirmado')

    onroute_date = fields.Datetime('Fecha En Ruta')

    finish_date = fields.Datetime('Fecha Finalizado')

    draft_to_confirm = fields.Char('Borrador a Confirmado')

    confirm_to_onroute = fields.Char('Confirmado a En Ruta')

    onroute_to_finish = fields.Char('En Ruta a Finalizado')

    payment_method = fields.Many2one('pos.payment.method','Metodo de Pago')

    change = fields.Float('Vuelto')

    warehouse_id = fields.Many2one('stock.warehouse', 'Bodega')

    location_id = fields.Many2one(comodel_name='stock.location',string='Camion', domain=[('is_truck', '=', True)])

    truck_ids = fields.Many2many('stock.location', 'Camiones', compute='compute_truck_ids')

    is_loan = fields.Boolean('Es Prestamo')

    products = fields.Many2many('product.template','available_in_pos')

    total_untaxed = fields.Monetary('Base Imponible', compute='onchange_mobile_line')

    total_taxes = fields.Monetary('Impuestos', compute='onchange_mobile_line')

    @api.onchange('mobile_lines')
    def onchange_mobile_line(self):
        for item in self:
            total_untax = []
            total_tax = []
            for line in item.mobile_lines:
                total_untax.append(line.price * line.qty)
                for tx in line.tax_ids:
                    total_tax.append((tx.amount/100) * line.price * line.qty)
            if len(total_untax) > 0:
                item.write({
                    'total_sale': sum(total_untax) + sum(total_tax),
                    'total_untaxed': sum(total_untax),
                    'total_taxes': sum(total_tax)
                })
            else:
                item.write({
                    'total_sale': 0,
                    'total_untaxed': 0,
                    'total_taxes': 0
                })

    @api.onchange('customer_id')
    def onchange_customer_id(self):
        self.price_list_id = self.customer_id.property_product_pricelist

    @api.onchange('seller_id')
    def onchange_location_id(self):
        if self.seller_id:
            stock_quant = self.env['stock.quant'].search([('location_id.id','=',self.seller_id.truck_id.id)])
            if stock_quant:
                self.location_id = self.seller_id.truck_id
            else:
                raise models.ValidationError('Este camion no tiene stock suficiente')
        for item in self:
            warehouses = self.env['stock.warehouse'].search([])
            for ware in warehouses:
                trucks = ware.mapped('truck_ids').mapped('id')
                if item.seller_id.truck_id.id in trucks:
                    item.warehouse_id = ware
                    break

    def compute_truck_ids(self):
        products_line = self.mobile_lines.mapped('product_id').mapped('id')
        stock_quant = self.env['stock.quant'].search([('product_id.id', 'in', products_line)]).mapped(
            'location_id').filtered(lambda a: a.is_truck)
        self.truck_ids = stock_quant


    @api.onchange('paid')
    def compute_change(self):
        for item in self:
            if item.state == 'onroute':
                if item.total_sale > 0:
                    change = item.paid - item.total_sale
                    if change > 0:
                        item.change = change

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
        self.confirm_date = datetime.datetime.now()
        datedif = relativedelta(self.confirm_date, self.create_date)
        strdate = ""
        if datedif.years != 0:
            strdate = '{} años'.format(datedif.years)

        if datedif.months != 0:
            strdate = '{} {} meses'.format(strdate, datedif.months)

        if datedif.days != 0:
            strdate = '{} {} dias'.format(strdate, datedif.days)

        if datedif.hours != 0:
            strdate = '{} {} hr'.format(strdate, datedif.hours)

        if datedif.minutes != 0:
            strdate = '{} {} min'.format(strdate, datedif.minutes)

        if datedif.seconds != 0:
            strdate = '{} {} seg'.format(strdate, datedif.seconds)

        self.draft_to_confirm = strdate

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
        self.onroute_date = datetime.datetime.now()
        datedif =  relativedelta(self.onroute_date, self.confirm_date)
        strdate = ""
        if datedif.years != 0:
            strdate = '{} años'.format(datedif.years)

        if datedif.months != 0:
            strdate = '{} {} meses'.format(strdate, datedif.months)

        if datedif.days != 0:
            strdate = '{} {} dias'.format(strdate, datedif.days)

        if datedif.hours != 0:
            strdate = '{} {} hr'.format(strdate, datedif.hours)

        if datedif.minutes != 0:
            strdate = '{} {} min'.format(strdate, datedif.minutes)

        if datedif.seconds != 0:
            strdate = '{} {} seg'.format(strdate, datedif.seconds)

        self.confirm_to_onroute = strdate

    def cancel_order(self):
        self.write({
            'state': 'cancel'
        })

    def make_done(self):
        if self.address_id:
            sale_odoo = self.env['sale.order'].create({
                'company_id': self.env.user.company_id.id,
                'currency_id': self.currency_id.id,
                'partner_id': self.address_id.id,
                'picking_policy': 'direct',
                'origin': self.id,
                'with_delivery': True,
                'loan_supply': self.is_loan,
                'warehouse_id': self.warehouse_id.id,
                'pricelist_id': self.price_list_id.id
            })
        else:
            sale_odoo = self.env['sale.order'].create({
                'company_id': self.env.user.company_id.id,
                'currency_id': self.currency_id.id,
                'partner_id': self.customer_id.id,
                'picking_policy': 'direct',
                'origin': self.id,
                'with_delivery': True,
                'loan_supply': self.is_loan,
                'warehouse_id': self.warehouse_id.id,
                'pricelist_id': self.price_list_id.id
            })

        for line in self.mobile_lines:
            sale_line = self.env['sale.order.line'].create({
                'product_id': line.product_id.id,
                'order_id': sale_odoo.id,
                'customer_lead': 1,
                'name': sale_odoo.name,
                'price_unit': line.price,
                'product_uom_qty': line.qty,
            })
            for tx in line.tax_ids:
                if tx.id not in sale_line.mapped('tax_id').mapped('id'):
                    sale_line.write({
                        'tax_id': [(4, tx.id)]
                    })
        sale_odoo.action_confirm()

        for stock in sale_odoo.picking_ids[0].move_line_ids_without_package:
            stock.write({
                'qty_done': self.mobile_lines.filtered(lambda a: a.product_id.id == stock.product_id.id).qty,
                'location_id':self.location_id.id,
            })

        for line in self.mobile_lines:
            if line.loan_qty > 0:
                for move in sale_odoo.picking_ids[0].move_ids_without_package:
                    move.write({
                        'loan_supply': self.mobile_lines.filtered(lambda a: a.product_id.id == move.product_id.id).loan_qty,
                    })

        sale_odoo.picking_ids[0].write({
            'show_supply': True,
            'location_id': self.location_id.id
        })
        sale_odoo.picking_ids[0].button_validate()
        sale_odoo.picking_ids[0].supply_dispatch_id.write({
            'location_dest_id':self.location_id.id,
        })
        sale_odoo.picking_ids[0].supply_dispatch_id.move_line_ids_without_package.write({
            'location_dest_id':self.location_id.id,

        })
        sale_odoo.picking_ids[0].loan_reception_id.action_confirm()
        sale_odoo.picking_ids[0].loan_reception_id.button_validate()
        for mobile in self.mobile_lines:
            sale_odoo.picking_ids[0].supply_dispatch_id.move_line_ids_without_package.filtered(lambda a: a.product_id.id == mobile.product_id.supply_id.id).write({
                'qty_done' : sale_odoo.picking_ids[0].supply_dispatch_id.move_line_ids_without_package.filtered(lambda a: a.product_id.id == mobile.product_id.supply_id.id).qty_done - mobile.loan_qty
            })
        sale_odoo._create_invoices()
        sale_odoo.invoice_ids[0].action_post()
        self.write({
            'sale_id': sale_odoo.id,
            'state': 'done'
        })
        self.finish_date = datetime.datetime.now()
        datedif = relativedelta(self.finish_date, self.onroute_date)
        strdate = ""
        if datedif.years != 0:
            strdate = '{} años'.format(datedif.years)

        if datedif.months != 0:
            strdate = '{} {} meses'.format(strdate, datedif.months)

        if datedif.days != 0:
            strdate = '{} {} dias'.format(strdate, datedif.days)

        if datedif.hours != 0:
            strdate = '{} {} hr'.format(strdate, datedif.hours)

        if datedif.minutes != 0:
            strdate = '{} {} min'.format(strdate, datedif.minutes)

        if datedif.seconds != 0:
            strdate = '{} {} seg'.format(strdate, datedif.seconds)
        self.onroute_to_finish = strdate





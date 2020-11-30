from odoo import fields, models, api


class MobileSaleOrder(models.Model):
    _name = 'mobile.sale.order'

    name = fields.Char('Nombre', readonly=1)

    state = fields.Selection(
        [('cancel', 'Cancelado'), ('draft', 'Borrador'), ('confirm', 'Confirmado'), ('onroute', 'En Ruta'),
         ('done', 'Hecha')], default='draft', string='Estado')

    customer_id = fields.Many2one('res.partner', 'Cliente', required=True)

    address_id = fields.Many2one('res.partner', 'Direccion de envio')

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

    change = fields.Float('Vuelto')

    warehouse_id = fields.Many2one('stock.warehouse', 'Bodega')

    location_id = fields.Many2one(comodel_name='stock.location',string='Camion', domain=[('is_truck', '=', True)])

    truck_ids = fields.Many2many('stock.location', 'Camiones', compute='compute_truck_ids')

    is_loan = fields.Boolean('Es Prestamo')

    products = fields.Many2many('product.template','available_in_pos')

    @api.onchange('mobile_lines')
    def onchange_mobile_line(self):
        for item in self:
            if item.state != 'done'
                total = []
                for line in item.mobile_lines:
                    total.append(line.subtotal)
                item.total_sale = sum(total)

    @api.onchange('price_list_id')
    def onchange_product_price(self):
        for item in self.price_list_id.item_ids:
            self.mobile_lines.filtered(lambda a: item.product_tmpl_id.id == a.product_id.id).write({
                'price': item.fixed_price
            })

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
            self.env['sale.order.line'].create({
                'product_id': line.product_id.id,
                'order_id': sale_odoo.id,
                'customer_lead': 1,
                'name': sale_odoo.name,
                'price_unit': line.price,
                'product_uom_qty': line.qty,
            })
        sale_odoo.action_confirm()

        for stock in sale_odoo.picking_ids[0].move_line_ids_without_package:
            stock.write({
                'qty_done': self.mobile_lines.filtered(lambda a: a.product_id.id == stock.product_id.id).qty,
                'location_id':self.location_id.id,
            })
        if self.is_loan:
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
        sale_odoo._create_invoices()
        sale_odoo.invoice_ids[0].action_post()
        self.write({
            'sale_id': sale_odoo.id,
            'state': 'done'
        })

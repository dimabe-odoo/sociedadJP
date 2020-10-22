from odoo import fields, models, api
import datetime


class MobileSaleOrder(models.Model):
    _name = 'mobile.sale.order'

    name = fields.Char('Nombre', readonly=1)

    state = fields.Selection([('draft','Borrador'),('progress', 'En Progeso'), ('done', 'Hecha')])

    customer_id = fields.Many2one('res.partner', 'Cliente')

    address_id = fields.Many2one('res.partner','Direccion de envio')

    address_ids = fields.Many2many('res.partner','Direcciones del cliente',compute='compute_address_ids')

    price_list_id = fields.Many2one('product.pricelist','Lista de Precio del Cliente') 

    saleman_id = fields.Many2one('res.partner', 'Vendedor')

    date_done = fields.Datetime('Fecha de entrega')

    mobile_lines = fields.One2many('mobile.sale.line', 'mobile_id', 'Productos')

    total_sale = fields.Monetary('Total')

    currency_id = fields.Many2one('res.currency', 'Moneda',
                                  default=lambda self: self.env['res.currency'].search([('name', '=', 'CLP')]))

    sale_id = fields.Many2one('sale.order', 'Venta Interna')

    location_id = fields.Many2one('stock.location', 'Ubicacion')

    is_loan = fields.Boolean('Es Prestamo')

    date_done = fields.Datetime('Fecha de Realizado')

    @api.onchange('address_id')
    def compute_address_ids(self):
        for item in self:
            self.address_id = self.env['res.partner'].search([('id','in',self.customer_id.child_ids.mapped('id'))])

    @api.model
    def create(self, values):
        values['state'] = 'draft'
        values['name'] = self.env['ir.sequence'].next_by_code('mobile.sale.order')
        return super(MobileSaleOrder, self).create(values)

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
            'with_delivery':True,
            'loan_supply':loan
        })
        self.write({
            'state': 'done',
            'date_done': datetime.datetime.now(),
            'sale_id': sale_odoo.id
        })
        self.mobile_lines.write({
            'state': 'done'
        })

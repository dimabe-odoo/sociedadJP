import datetime

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    supply_dispatch_id = fields.Many2one('stock.picking', 'Movimiento de insumos:')

    purchase_without_supply = fields.Boolean(string='Compra Como dato')

    sale_with_rent = fields.Boolean(string='Préstamo de cilindros')

    show_supply = fields.Boolean(string='Mostrar Despacho de insumo')

    have_supply = fields.Boolean(string='Tiene Insumos', compute='compute_have_supply')

    loan_reception_id = fields.Many2one('stock.picking', 'Prestamo de insumos')

    @api.onchange('move_ids_without_package')
    def compute_have_supply(self):
        for item in self:
            item.have_supply = bool(item.move_ids_without_package.mapped('product_id').mapped('supply_id'))

    def button_validate(self):
        for item in self:
            if item.picking_type_code not in ('outgoing','incoming'):
                return super(StockPicking,self).button_validate()
            else:
                models._logger.error(self.name)

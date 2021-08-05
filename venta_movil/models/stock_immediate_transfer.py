from odoo import fields, models, api
from py_linq import Enumerable


class StockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'

    def process(self):
        res = super(StockImmediateTransfer, self).process()
        if Enumerable(self.pick_ids).all(lambda x: x.state == 'done'):
            for pick in self.pick_ids:
                pick.process_supply_movement()
        return res

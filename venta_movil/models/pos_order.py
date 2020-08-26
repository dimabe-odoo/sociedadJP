from odoo import fields, models, api


class PosOrder (models.Model):
    _inherit = 'pos.order'

    def create(self,values):
        models._logger.error(values.keys())
        models._logger.error(values.values())
        super(PosOrder, self).create()
    



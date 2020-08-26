from odoo import fields, models, api


class PosPopUp(models.Model):
    _name = 'pos.popups'
    _description = 'Description'

    name = fields.Char('Name', size=30, required=True)

    def refresh(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

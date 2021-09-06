from odoo import http
from odoo.http import request
import werkzeug

class CommuneController(http.Controller):

    @http.route('/api/get_communes', type='json', methods=['GET', 'POST'], auth='public', cors='*')
    def get_communes(self):
        communes = request.env['jp.commune'].sudo().search([('state_id', '=', 1176)], order='name asc')
        result = []
        for res in communes:
            result.append({
                'id': res.id,
                'name': res.name
                })
        return result
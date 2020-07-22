from odoo import http
from odoo.http import request
import werkzeug

class CommuneController(http.Controller):

    @http.route('/api/communes', type='json', methods=['GET'], auth='public', cors='*')
    def get_communes(self):
        communes = request.env['jp.commune'].sudo().search([])
        result = []
        for res in communes:
            result.append({'name': res.name})
        return result
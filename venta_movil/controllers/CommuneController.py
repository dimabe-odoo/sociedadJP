from odoo import http
from odoo.http import request
import werkzeug

class CommuneController(http.Controller):

    @http.route('/api/communes', type='json', methods=['GET'], auth='token', cors='*')
    def do_user(self):
        communes = request.env['jp.commune'].sudo().search_read([('state_id', '=', 1176)], ['name'])
        return {'communes': communes}
from odoo import http
from odoo.http import request
import werkzeug

class ProfileController(http.Controller):

    @http.route('/api/user', type='json', methods=['GET'], auth='token', cors='*')
    def do_user(self):
        user = request.env['res_users'].sudo().search_read([('id', '=', request.uid)], ['name', 'login'])
        return {'user': user}
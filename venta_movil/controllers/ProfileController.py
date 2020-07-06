from odoo import http
from odoo.http import request
import werkzeug

class ProfileController(http.Controller):

    @http.route('/api/user', type='json', auth='token', cors='*')
    def do_user(self, uemail):
        return {'bad': uemail}
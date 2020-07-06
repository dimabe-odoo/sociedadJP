from odoo import http
from odoo.http import request
from ..jwt_token import generate_token
import werkzeug

class ProfileController(http.Controller):

    @http.route('/api/user', type='json', auth='token', cors='*')
    def get_user(self):
        user = request.uid
        return {'user': user}
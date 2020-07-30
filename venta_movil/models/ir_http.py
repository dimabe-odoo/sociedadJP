from odoo import exceptions, models
from odoo.http import request
import jwt
from ..jwt_token import decode_token, generate_token


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _auth_method_token(cls):
        token = request.httprequest.headers.get('authorization', '', type=str)
        userId = request.uid
        if token:
            token = token.split(' ')[1]
            try:
                payload = decode_token(token)
                if 'sub' in payload:
                    u = request.env['res.users'].sudo().search(
                        [('id', '=', int(payload['sub']))]
                    )
                    request.uid = u.id
                    request.uemail = u.login
            except jwt.ExpiredSignatureError:
               token = generate_token(userId)
               return {'new-token': token}
        else:
            raise exceptions.AccessDenied()
# -*- coding: utf-8 -*-
# from odoo import http


# class MapsOdoo(http.Controller):
#     @http.route('/maps_odoo/maps_odoo/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/maps_odoo/maps_odoo/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('maps_odoo.listing', {
#             'root': '/maps_odoo/maps_odoo',
#             'objects': http.request.env['maps_odoo.maps_odoo'].search([]),
#         })

#     @http.route('/maps_odoo/maps_odoo/objects/<model("maps_odoo.maps_odoo"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('maps_odoo.object', {
#             'object': obj
#         })

# -*- coding: utf-8 -*-
# from odoo import http


# class RgbMrpCustom(http.Controller):
#     @http.route('/rgb_mrp_custom/rgb_mrp_custom', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rgb_mrp_custom/rgb_mrp_custom/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('rgb_mrp_custom.listing', {
#             'root': '/rgb_mrp_custom/rgb_mrp_custom',
#             'objects': http.request.env['rgb_mrp_custom.rgb_mrp_custom'].search([]),
#         })

#     @http.route('/rgb_mrp_custom/rgb_mrp_custom/objects/<model("rgb_mrp_custom.rgb_mrp_custom"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rgb_mrp_custom.object', {
#             'object': obj
#         })

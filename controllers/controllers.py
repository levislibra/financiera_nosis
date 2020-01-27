# -*- coding: utf-8 -*-
from openerp import http

# class FinancieraNosis(http.Controller):
#     @http.route('/financiera_nosis/financiera_nosis/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/financiera_nosis/financiera_nosis/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('financiera_nosis.listing', {
#             'root': '/financiera_nosis/financiera_nosis',
#             'objects': http.request.env['financiera_nosis.financiera_nosis'].search([]),
#         })

#     @http.route('/financiera_nosis/financiera_nosis/objects/<model("financiera_nosis.financiera_nosis"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('financiera_nosis.object', {
#             'object': obj
#         })
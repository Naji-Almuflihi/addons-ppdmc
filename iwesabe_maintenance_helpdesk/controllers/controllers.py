# -*- coding: utf-8 -*-
# from odoo import http


# class IwesabeMaintenanceHelpdesk(http.Controller):
#     @http.route('/iwesabe_maintenance_helpdesk/iwesabe_maintenance_helpdesk/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/iwesabe_maintenance_helpdesk/iwesabe_maintenance_helpdesk/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('iwesabe_maintenance_helpdesk.listing', {
#             'root': '/iwesabe_maintenance_helpdesk/iwesabe_maintenance_helpdesk',
#             'objects': http.request.env['iwesabe_maintenance_helpdesk.iwesabe_maintenance_helpdesk'].search([]),
#         })

#     @http.route('/iwesabe_maintenance_helpdesk/iwesabe_maintenance_helpdesk/objects/<model("iwesabe_maintenance_helpdesk.iwesabe_maintenance_helpdesk"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('iwesabe_maintenance_helpdesk.object', {
#             'object': obj
#         })

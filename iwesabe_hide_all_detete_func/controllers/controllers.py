# -*- coding: utf-8 -*-
# from odoo import http


# class HideAllDeteteFunc(http.Controller):
#     @http.route('/hide_all_detete_func/hide_all_detete_func/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hide_all_detete_func/hide_all_detete_func/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hide_all_detete_func.listing', {
#             'root': '/hide_all_detete_func/hide_all_detete_func',
#             'objects': http.request.env['hide_all_detete_func.hide_all_detete_func'].search([]),
#         })

#     @http.route('/hide_all_detete_func/hide_all_detete_func/objects/<model("hide_all_detete_func.hide_all_detete_func"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hide_all_detete_func.object', {
#             'object': obj
#         })

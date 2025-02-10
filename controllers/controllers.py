# -*- coding: utf-8 -*-
# from odoo import http


# class EasyExams(http.Controller):
#     @http.route('/easy_exams/easy_exams', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/easy_exams/easy_exams/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('easy_exams.listing', {
#             'root': '/easy_exams/easy_exams',
#             'objects': http.request.env['easy_exams.easy_exams'].search([]),
#         })

#     @http.route('/easy_exams/easy_exams/objects/<model("easy_exams.easy_exams"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('easy_exams.object', {
#             'object': obj
#         })


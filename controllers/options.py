# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessDenied
from .auth import JWTAuth
from ._helpers import _http_success_response, _http_error_response, _error_response, _success_response

import logging

_logger = logging.getLogger(__name__)

class QuestionOptionAPI(http.Controller):
    ## 🔹 [GET] Retrieve Options for a Question
    @http.route('/api/exams/questions/options/<int:question_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_question_options(self, question_id, **kwargs):
        """Retrieve all options for a given question (JWT required, user must have access to the exam)"""
        try:
            user_data = JWTAuth.authenticate_request()
            user_id = user_data.get("user_id")

            question = request.env['easy_exams.question'].sudo().browse(question_id)
            if not question.exists() or user_id not in question.exam_id.course_id.user_ids.ids:
                return _http_error_response("Unauthorized: Access Denied", 403)

            options = request.env['easy_exams.question_option'].sudo().search([('question_id', '=', question_id)])

            option_data = [
                {'id': opt.id, 
                 'content': opt.content, 
                 'is_correct': opt.is_correct} for opt in options]

            return _http_success_response(option_data, "Options retrieved successfully")
        except AccessDenied:
            return _http_error_response("Unauthorized: Access Denied", 401)
        except Exception as e:
            _logger.error(f"Error retrieving options: {str(e)}")
            return _http_error_response(f"Error retrieving options: {str(e)}", 500)

    ## 🔹 [POST] Create a New Option
    @http.route('/api/exams/questions/options/create', type='jsonrpc', auth='public', methods=['POST'], csrf=False)
    def create_question_option(self, **kwargs):
        """Create a new question option (JWT required, user must have access to the exam)"""
        try:
            user_data = JWTAuth.authenticate_request()
            user_id = user_data.get("user_id")

            question_id = kwargs.get('question_id')
            content = kwargs.get('content')
            is_correct = kwargs.get('is_correct', False)

            if not question_id or not content:
                return _error_response("Missing required fields", 400)

            question = request.env['easy_exams.question'].sudo().browse(question_id)
            if not question.exists() or user_id not in question.exam_id.course_id.user_ids.ids:
                return _error_response("Unauthorized: Access Denied", 403)

            option = request.env['easy_exams.question_option'].sudo().create({
                'question_id': question_id,
                'content': content,
                'is_correct': is_correct or False,
            })

            return _success_response({'id': option.id, 'content': option.content}, "Option created successfully")
        except AccessDenied:
            return _error_response("Unauthorized: Access Denied", 401)
        except Exception as e:
            _logger.error(f"Error creating option: {str(e)}")
            return _error_response(f"Error creating option: {str(e)}", 500)
        
    ## 🔹 [PUT] Update a Question Option
    @http.route('/api/exams/question_options/update/<int:option_id>', type='jsonrpc', auth='public', methods=['PUT'], csrf=False)
    def update_question_option(self, option_id, **kwargs):
        """
        Update an existing question option (JWT required)
        """
        try:
            user_data = JWTAuth.authenticate_request()
            user_id = user_data.get("user_id")

            option = request.env['easy_exams.question_option'].sudo().browse(option_id)

            if not option.exists() or not option.question_id or not option.question_id.exam_id or not option.question_id.exam_id.course_id or user_id not in option.question_id.exam_id.course_id.user_ids.ids:
                return _error_response("Unauthorized: Access Denied", 403)

            option.write({
                'content': kwargs.get('content', option.content),
                'is_correct': kwargs.get('is_correct', option.is_correct),
            })

            return _success_response({'id': option.id, 'content': option.content}, "Option updated successfully.")

        except AccessDenied:
            return _error_response("Unauthorized: Access Denied", 401)
        except Exception as e:
            _logger.error(f"Error updating option: {str(e)}")
            return _error_response(f"Error updating option: {str(e)}", 500)
    
    ## 🔹 [DELETE] Delete an Option
    @http.route('/api/exams/questions/options/delete/<int:option_id>', type='http', auth='public', methods=['DELETE'], csrf=False)
    def delete_question_option(self, option_id, **kwargs):
        """Delete a question option (JWT required, user must have access to the exam)"""
        try:
            user_data = JWTAuth.authenticate_request()
            user_id = user_data.get("user_id")

            option = request.env['easy_exams.question_option'].sudo().browse(option_id)
            if not option.exists() or user_id not in option.question_id.exam_id.course_id.user_ids.ids:
                return _http_error_response("Unauthorized: Access Denied", 403)

            option.unlink()

            return _http_success_response({}, "Option deleted successfully")
        except AccessDenied:
            return _http_error_response("Unauthorized: Access Denied", 401) 
        except Exception as e:
            _logger.error(f"Error deleting option: {str(e)}")
            return _http_error_response(f"Error deleting option: {str(e)}", 500)

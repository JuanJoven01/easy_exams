# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessDenied
from .auth import JWTAuth
from ._helpers import _http_success_response, _http_error_response, _error_response, _success_response

import logging

_logger = logging.getLogger(__name__)

class QuestionPairAPI(http.Controller):

    ## 🔹 [GET] Retrieve Pairs for a Question
    @http.route('/api/exams/questions/pairs/<int:question_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_question_pairs(self, question_id, **kwargs):
        """Retrieve all pairs for a given question (JWT required, user must have access to the exam)"""
        try:
            user_data = JWTAuth.authenticate_request()
            user_id = user_data.get("user_id")

            question = request.env['easy_exams.question'].sudo().browse(question_id)
            if not question.exists() or user_id not in question.exam_id.course_id.user_ids.ids:
                return _http_error_response("Unauthorized: Access Denied", 403)

            pairs = request.env['easy_exams.question_pair'].sudo().search([('question_id', '=', question_id)])

            pair_data = [{'id': pair.id, 'term': pair.term, 'match': pair.match} for pair in pairs]

            return _http_success_response(pair_data, "Pairs retrieved successfully")
        except AccessDenied:
            return _http_error_response("Unauthorized: Access Denied", 401)
        except Exception as e:
            _logger.error(f"Error retrieving pairs: {str(e)}")
            return _http_error_response(f"Error retrieving pairs: {str(e)}", 500)
 
    ## 🔹 [POST] Create a New Pair
    @http.route('/api/exams/questions/pairs/create', type='json', auth='public', methods=['POST'], csrf=False)
    def create_question_pair(self, **kwargs):
        """Create a new question pair (JWT required, user must have access to the exam)"""
        try:
            user_data = JWTAuth.authenticate_request()
            user_id = user_data.get("user_id")

            question_id = kwargs.get('question_id')
            term = kwargs.get('term')
            match = kwargs.get('match')

            if not question_id or not term or not match:
                return _error_response("Missing required fields", 400)

            question = request.env['easy_exams.question'].sudo().browse(question_id)
            if not question.exists() or user_id not in question.exam_id.course_id.user_ids.ids:
                return _error_response("Unauthorized: Access Denied", 403)

            pair = request.env['easy_exams.question_pair'].sudo().create({
                'question_id': question_id,
                'term': term,
                'match': match,
            })

            return _success_response({'id': pair.id, 'term': pair.term}, "Pair created successfully")
        except AccessDenied:
            return _error_response("Unauthorized: Access Denied", 401)
        except Exception as e:
            _logger.error(f"Error creating pair: {str(e)}")
            return _error_response(f"Error creating pair: {str(e)}", 500)

    ## 🔹 [PUT] Update a Question Pair
    @http.route('/api/exams/question_pairs/update', type='json', auth='public', methods=['PUT'], csrf=False)
    def update_question_pair(self, **kwargs):
        """
        Update an existing question pair (JWT required)
        """
        try:
            user_data = JWTAuth.authenticate_request()
            user_id = user_data.get("user_id")
            pair_id = kwargs.get('pair_id')
            if not pair_id:
                return _error_response('Pair id is required', 400)

            pair = request.env['easy_exams.question_pair'].sudo().browse(pair_id)

            print('pair.question_id.exam_id.course_id.user_ids' *2)
            print(pair.question_id.exam_id.course_id.user_ids)

            if not pair.exists() or not pair.question_id or not pair.question_id.exam_id or not pair.question_id.exam_id.course_id or user_id not in pair.question_id.exam_id.course_id.user_ids.ids:
                return _error_response("Unauthorized: Access Denied", 403)

            pair.write({
                'term': kwargs.get('term', pair.term),
                'match': kwargs.get('match', pair.match),
            })

            return _success_response({'id': pair.id, 'term': pair.term}, "Pair updated successfully.")

        except AccessDenied:
            return _error_response("Unauthorized: Access Denied", 401)
        except Exception as e:
            _logger.error(f"Error updating pair: {str(e)}")
            return _error_response(f"Error updating pair: {str(e)}", 500)
        
    ## 🔹 [DELETE] Delete a Pair
    @http.route('/api/exams/questions/pairs/delete/<int:pair_id>', type='http', auth='public', methods=['DELETE'], csrf=False)
    def delete_question_pair(self, pair_id, **kwargs):
        """Delete a question pair (JWT required, user must have access to the exam)"""
        try:
            user_data = JWTAuth.authenticate_request()
            user_id = user_data.get("user_id")

            pair = request.env['easy_exams.question_pair'].sudo().browse(pair_id)
            if not pair.exists() or user_id not in pair.question_id.exam_id.course_id.user_ids.ids:
                return _http_error_response("Unauthorized: Access Denied", 403)

            pair.unlink()

            return _http_success_response({}, "Pair deleted successfully")
        except AccessDenied:
            return _http_error_response("Unauthorized: Access Denied", 401)
        except Exception as e:
            _logger.error(f"Error deleting pair: {str(e)}")
            return _http_error_response(f"Error deleting pair: {str(e)}", 500)

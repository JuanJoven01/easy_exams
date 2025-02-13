# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessDenied, ValidationError
from .auth import JWTAuth
from ._helpers import _http_success_response, _http_error_response, _error_response, _success_response
import logging

_logger = logging.getLogger(__name__)

class QuestionAPI(http.Controller):

    ## 🔹 [GET] Retrieve Questions by Exam ID
    @http.route('/api/exams/questions/<int:exam_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_questions(self, exam_id, **kwargs):
        """
        Retrieve questions filtered by exam_id (JWT required)
        """
        try:
            user_data = JWTAuth.authenticate_request()
            user_id = user_data.get("user_id")

            # Ensure exam_id is provided
            if not exam_id:
                return _http_error_response("Missing exam_id parameter", 400)

            # Check if user has access to the exam
            exam = request.env['easy_exams.exam'].sudo().search([
                ('id', '=', exam_id),
                ('course_id.user_ids', 'in', [user_id])
            ], limit=1)

            if not exam:
                return _http_error_response("Exam not found or unauthorized", 404)

            # Fetch questions for the exam
            questions = request.env['easy_exams.question'].sudo().search([('exam_id', '=', exam_id)])

            question_data = [{
                'id': q.id,
                'exam_id': q.exam_id.id,
                'question_type': q.question_type,
                'content': q.content,
                'image': q.image,
                'correct_answer': q.correct_answer,
                'options': [{'id': opt.id, 'content': opt.content, 'is_correct': opt.is_correct} for opt in q.option_ids],
                'pairs': [{'id': pair.id, 'term': pair.term, 'match': pair.match} for pair in q.pair_ids]
            } for q in questions]

            return _http_success_response(question_data, "Questions retrieved successfully")
        except AccessDenied:
            return _http_error_response("Unauthorized: Access Denied", 403)
        except Exception as e:
            _logger.error(f"Error retrieving questions: {str(e)}")
            return _http_error_response(f"Error retrieving questions: {str(e)}", 500)

    ## 🔹 [POST] Create a New Question
    @http.route('/api/exams/questions/create', type='jsonrpc', auth='public', methods=['POST'], csrf=False)
    def create_question(self, **kwargs):
        """
        Create a new question under an authorized exam (JWT required)
        """
        try:
            user_data = JWTAuth.authenticate_request()
            user_id = user_data.get("user_id")

            # Validate required fields
            exam_id = kwargs.get('exam_id')
            question_type = kwargs.get('question_type')
            content = kwargs.get('content')

            if not exam_id or not question_type or not content:
                return _error_response("Missing required fields", 400)

            # Check if user has access to the exam
            exam = request.env['easy_exams.exam'].sudo().search([
                ('id', '=', exam_id),
                ('course_id.user_ids', 'in', [user_id])
            ], limit=1)

            if not exam:
                return _error_response("Exam not found or unauthorized", 400)

            # Create new question
            new_question = request.env['easy_exams.question'].sudo().create({
                'exam_id': exam.id,
                'question_type': question_type,
                'content': content,
                'image': kwargs.get('image') or False,
                'correct_answer': kwargs.get('correct_answer', ''),
            })

            return _success_response({'id': new_question.id, 'content': new_question.content}, "Question created successfully")
        except ValidationError as e:
            return _error_response(str(e), 400)
        except AccessDenied:
            return _error_response("Unauthorized: Access Denied", 403)
        except Exception as e:
            _logger.error(f"Error creating question: {str(e)}")
            return _error_response(f"Error creating question: {str(e)}", 500)

    ## 🔹 [PUT] Update a Question
    @http.route('/api/exams/questions/update', type='jsonrpc', auth='public', methods=['PUT'], csrf=False)
    def update_question(self, **kwargs):
        """
        Update an existing question (JWT required)
        """
        try:
            user_data = JWTAuth.authenticate_request()
            user_id = user_data.get("user_id")

            question_id = kwargs.get('question_id')
            if not question_id:
                return _error_response('Question id is required', 400)

            # Find the question
            question = request.env['easy_exams.question'].sudo().search([
                ('id', '=', question_id),
                ('exam_id.course_id.user_ids', 'in', [user_id])
            ], limit=1)

            if not question:
                return _error_response("Question not found or unauthorized", 400)

            update_data = {
                'question_type': kwargs.get('question_type', question.question_type),
                'content': kwargs.get('content', question.content),
                'image': kwargs.get('image', question.image),
                'correct_answer': kwargs.get('correct_answer', question.correct_answer),
            }

            question.sudo().write(update_data)

            return _success_response(update_data, "Question updated successfully")
        except ValidationError as e:
            return _error_response(str(e), 400)
        except AccessDenied:
            return _error_response("Unauthorized: Access Denied", 403)
        except Exception as e:
            _logger.error(f"Error updating question: {str(e)}")
            return _error_response(f"Error updating question: {str(e)}", 500)

    ## 🔹 [DELETE] Delete a Question
    @http.route('/api/exams/questions/delete/<int:question_id>', type='http', auth='public', methods=['DELETE'], csrf=False)
    def delete_question(self, question_id, **kwargs):
        """
        Delete a question (JWT required)
        """
        try:
            user_data = JWTAuth.authenticate_request()
            user_id = user_data.get("user_id")

            # Find the question
            question = request.env['easy_exams.question'].sudo().search([
                ('id', '=', question_id),
                ('exam_id.course_id.user_ids', 'in', [user_id])
            ], limit=1)

            if not question:
                return _http_error_response("Question not found or unauthorized", 404)

            question.sudo().unlink()

            return _http_success_response({'id': question_id}, "Question deleted successfully")
        except AccessDenied:
            return _http_error_response("Unauthorized: Access Denied", 403)
        except Exception as e:
            _logger.error(f"Error deleting question: {str(e)}")
            return _http_error_response(f"Error deleting question: {str(e)}", 500)

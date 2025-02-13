# -*- coding: utf-8 -*-
from odoo import http, fields
from odoo.http import request
from odoo.exceptions import AccessDenied, ValidationError
from .auth import JWTAuth
from ._helpers import _http_success_response, _http_error_response, _error_response, _success_response
import logging, datetime

_logger = logging.getLogger(__name__)

class ExamAttemptAPI(http.Controller):

    ## 🔹 [GET] Retrieve Exam Attempts (Filtered by Exam ID)
    @http.route('/api/exams/attempts/get/<int:exam_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_exam_attempts(self, exam_id, **kwargs):
        """
        Retrieve exam attempts, optionally filtered by exam_id (JWT required)
        """
        try:
            user_data = JWTAuth.authenticate_request()
            user_id = user_data.get("user_id")
            domain = [('exam_id.course_id.user_ids', 'in', user_id),('exam_id', '=', int(exam_id))]

            attempts = request.env['easy_exams.exam_attempt'].sudo().search(domain)

            return _http_success_response([{
                'id': attempt.id,
                'exam_id': attempt.exam_id.id,
                'student_name': attempt.student_name,
                'student_id': attempt.student_id,
                'start_time': attempt.start_time,
                'end_time': attempt.end_time,
                'score': attempt.score
            } for attempt in attempts], "Exam attempts retrieved successfully.")

        except AccessDenied:
            return _http_error_response("Unauthorized: Access Denied", 401)
        except Exception as e:
            _logger.error(f"Error retrieving exam attempts: {str(e)}")
            return _http_error_response(f"Error retrieving exam attempts: {str(e)}", 500)

    ## 🔹 [POST] Create a New Exam Attempt
    @http.route('/api/exams/attempts/create', type='jsonrpc', auth='public', methods=['POST'], csrf=False)
    def create_exam_attempt(self, **kwargs):
        """
        Create a new exam attempt (Public - No JWT Required)
        """
        try:
            student_name = kwargs.get('student_name')
            student_id = kwargs.get('student_id')
            access_code = kwargs.get('access_code')

            # Validate required fields
            if not student_name or not student_id or not access_code:
                return _error_response("Missing required fields", 400)

            # Search for the exam by access code
            exam = request.env['easy_exams.exam'].sudo().search([('access_code', '=', access_code)], limit=1)

            if not exam:
                return _error_response("Invalid access code or exam not found", 404)

            # Create a new attempt
            new_attempt = request.env['easy_exams.exam_attempt'].sudo().create({
                'exam_id': exam.id,
                'student_name': student_name,
                'student_id': student_id,
                'start_time': kwargs.get('start_time', fields.Datetime.now()),
                'end_time': kwargs.get('end_time', False),
                'score': kwargs.get('score', 0),
            })

            return _success_response({'exam_time' : exam.duration  ,'id': new_attempt.id, 'student_name': new_attempt.student_name}, "Exam attempt created successfully.")

        except Exception as e:
            _logger.error(f"Error creating exam attempt: {str(e)}")
            return _error_response(f"Error creating exam attempt: {str(e)}", 500)


    ## 🔹 [PUT] Update an Exam Attempt
    @http.route('/api/exams/attempts/update', type='jsonrpc', auth='public', methods=['PUT'], csrf=False)
    def update_exam_attempt(self, **kwargs):
        """
        Update an existing exam attempt (JWT required)
        """
        try:
            user_data = JWTAuth.authenticate_request()
            user_id = user_data.get("user_id")
            attempt_id = kwargs.get('attempt_id')
            if not attempt_id:
                return _error_response('Attempt id is required')
            
            attempt = request.env['easy_exams.exam_attempt'].sudo().browse(attempt_id)
            if not attempt.exists() or not attempt.exam_id or not attempt.exam_id.course_id or user_id not in attempt.exam_id.course_id.user_ids.ids:
                return _error_response("Unauthorized: Access Denied", 403)

            attempt.write({
                'student_name': kwargs.get('student_name', attempt.student_name),
                'student_id': kwargs.get('student_id', attempt.student_id),
                'start_time': kwargs.get('start_time', attempt.start_time),
                'end_time': kwargs.get('end_time', attempt.end_time),
                'score': kwargs.get('score', attempt.score),
            })

            return _success_response({'id': attempt.id, 'student_name': attempt.student_name}, "Exam attempt updated successfully.")

        except AccessDenied:
            return _error_response("Unauthorized: Access Denied", 401)
        except Exception as e:
            _logger.error(f"Error updating exam attempt: {str(e)}")
            return _error_response(f"Error updating exam attempt: {str(e)}", 500)

    ## 🔹 [PUT] Update an Exam Attempt finished
    @http.route('/api/exams/attempts/update/finished', type='jsonrpc', auth='public', methods=['PUT'], csrf=False)
    def update_exam_attempt_finished(self, **kwargs):
        """
        Update an existing exam attempt (JWT required)
        """
        try:
            attempt_id = kwargs.get('attempt_id')
            if not attempt_id:
                return _error_response('Attempt id is required')
            
            attempt = request.env['easy_exams.exam_attempt'].sudo().browse(attempt_id)
            if not attempt.exists():
                return _error_response('Exam attempt not found', 404)
            attempt.write({
                'end_time': kwargs.get('end_time', fields.Datetime.now())
            })

            return _success_response({'id': attempt.id, 'student_name': attempt.student_name}, "Exam attempt updated successfully.")

        except AccessDenied:
            return _error_response("Unauthorized: Access Denied", 401)
        except Exception as e:
            _logger.error(f"Error updating exam attempt: {str(e)}")
            return _error_response(f"Error updating exam attempt: {str(e)}", 500)

    ## 🔹 [DELETE] Delete an Exam Attempt
    @http.route('/api/exams/attempts/delete/<int:attempt_id>', type='http', auth='public', methods=['DELETE'], csrf=False)
    def delete_exam_attempt(self, attempt_id, **kwargs):
        """
        Delete an exam attempt (JWT required)
        """
        try:
            user_data = JWTAuth.authenticate_request()
            user_id = user_data.get("user_id")

            attempt = request.env['easy_exams.exam_attempt'].sudo().browse(attempt_id)

            if not attempt.exists() or not attempt.exam_id or not attempt.exam_id.course_id or user_id not in attempt.exam_id.course_id.user_ids.ids:
                return _http_error_response("Unauthorized: Access Denied", 403)

            attempt.unlink()

            return _http_success_response({'id': attempt_id}, "Exam attempt deleted successfully.")

        except AccessDenied:
            return _http_error_response("Unauthorized: Access Denied", 401)
        except Exception as e:
            _logger.error(f"Error deleting exam attempt: {str(e)}")
            return _http_error_response(f"Error deleting exam attempt: {str(e)}", 500)

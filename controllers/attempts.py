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
    @http.route('/api/exams/attempts/get/<int:exam_id>', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_exam_attempts(self, exam_id, **kwargs):
        """
        Retrieve exam attempts, optionally filtered by exam_id and date range (JWT required)
        """
        try:
            user_data = JWTAuth.authenticate_request()
            user_id = user_data.get("user_id")

            domain = [('exam_id.course_id.user_ids', 'in', user_id), ('exam_id', '=', exam_id)]

            start_date = kwargs.get('start_date')
            end_date = kwargs.get('end_date')

            if start_date:
                domain.append(('start_time', '>=', start_date))
            if end_date:
                domain.append(('start_time', '<=', end_date))

            attempts = request.env['easy_exams.exam_attempt'].sudo().search(domain)

            attempts_data = [{
                'id': attempt.id,
                'exam_id': attempt.exam_id.id,
                'student_name': attempt.student_name,
                'student_id': attempt.student_id,
                'start_time': attempt.start_time.isoformat() if attempt.start_time else None,
                'end_time': attempt.end_time.isoformat() if attempt.end_time else None,
                'score': attempt.score
            } for attempt in attempts]

            return _http_success_response(attempts_data, "Exam attempts retrieved successfully.")

        except AccessDenied:
            return _http_error_response("Unauthorized: Access Denied", 401)
        except Exception as e:
            _logger.error(f"Error retrieving exam attempts: {str(e)}")
            return _http_error_response(f"Error retrieving exam attempts: {str(e)}", 500)

    ## 🔹 [GET] Retrieve Exam Attempts (Filtered by Exam ID)
    @http.route('/api/exams/attempts/get_full/<int:exam_id>', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    def get_exam_attempts_data(self, exam_id, **kwargs):
        """
        Retrieve exam attempts, optionally filtered by exam_id and date range (JWT required)
        """
        try:
            user_data = JWTAuth.authenticate_request()
            user_id = user_data.get("user_id")

            domain = [('exam_id.course_id.user_ids', 'in', user_id), ('exam_id', '=', exam_id)]

            start_date = kwargs.get('start_date')
            end_date = kwargs.get('end_date')

            if start_date:
                domain.append(('start_time', '>=', start_date))
            if end_date:
                domain.append(('start_time', '<=', end_date))

            attempts = request.env['easy_exams.exam_attempt'].sudo().search(domain)

            attempts_data = [{
                'id': attempt.id,
                'exam_id': attempt.exam_id.id,
                'student_name': attempt.student_name,
                'student_id': attempt.student_id,
                'start_time': attempt.start_time.isoformat() if attempt.start_time else None,
                'end_time': attempt.end_time.isoformat() if attempt.end_time else None,
                'score': attempt.score,
                'answer_ids': [{
                        'question_id': ans.question_id.id,
                        # 'question': {
                        #     'id' : ans.question_id.id,
                        #     'question_type': ans.question_id.question_type,
                        #     'content': ans.question_id.content,
                        #     'image': ans.question_id.image.decode('utf-8') if ans.question_id.image else None,
                        #     'correct_answer': ans.question_id.correct_answer,
                        #     'options' : [{
                        #             'id' : opt.id,
                        #             'content' : opt.content,
                        #             'is_correct' : opt.is_correct,
                        #         }for opt in ans.question_id.option_ids],
                        #     'pairs': [{
                        #             'id' : pair.id,
                        #             'term' : pair.term,
                        #             'match' : pair.match,
                        #         } for pair in ans.question_id.pair_ids],
                        #  },
                        'selected_options': [{
                                'id': opt.id,
                                'option_id': opt.question_option.id,
                                'option_content': opt.question_option.content,
                                'is_correct': opt.question_option.is_correct,
                            }for opt in ans.selected_option_ids],
                        'answer_pairs': [{
                            'id': pair.id,
                            'question_pair_id': pair.question_pair_id.id,
                            'question_pair_term': pair.question_pair_id.term,
                            'question_pair_match': pair.question_pair_id.match,
                            'selected_match': pair.selected_match
                        }for pair in ans.answer_pair_ids],
                        'answer_text' : ans.answer_text,
                        'is_correct': ans.is_correct,
                        'q_score': ans.q_score
                        
                    } for ans in attempt.answer_ids],
            } for attempt in attempts]

            return _http_success_response(attempts_data, "Exam attempts retrieved successfully.")

        except AccessDenied:
            return _http_error_response("Unauthorized: Access Denied", 401)
        except Exception as e:
            _logger.error(f"Error retrieving exam attempts: {str(e)}")
            return _http_error_response(f"Error retrieving exam attempts: {str(e)}", 500)
        
    ## 🔹 [POST] Create a New Exam Attempt
    @http.route('/api/exams/attempts/create', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
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

            if exam.is_active == False:
                return _error_response("The exam is not available", 404)
                

            # Create a new attempt
            new_attempt = request.env['easy_exams.exam_attempt'].sudo().create({
                'exam_id': exam.id,
                'student_name': student_name,
                'student_id': student_id,
                'start_time': kwargs.get('start_time', fields.Datetime.now()),
                'end_time': kwargs.get('end_time', False),
                'score': kwargs.get('score', 0),
            })

            token_payload = {
                'student_id': student_id,
                'attempt_id': new_attempt.id,
                'exam_id': exam.id
            }

            jwt = JWTAuth.generate_attempt_token(token_payload, int(exam.duration))

            return _success_response({'exam_time' : exam.duration, 'exam_name' : exam.name  ,'attempt_id': new_attempt.id, 'student_name': new_attempt.student_name, 'token': jwt, 'start_time': new_attempt.start_time, 'end_time': new_attempt.end_time  }, "Exam attempt created successfully.")

        except Exception as e:
            _logger.error(f"Error creating exam attempt: {str(e)}")
            return _error_response(f"Error creating exam attempt: {str(e)}", 500)


    ## 🔹 [PUT] Update an Exam Attempt
    @http.route('/api/exams/attempts/update', type='json', auth='public', methods=['PUT'], csrf=False, cors="*")
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
    @http.route('/api/exams/attempts/update/finished', type='json', auth='public', methods=['PUT'], csrf=False, cors="*")
    def update_exam_attempt_finished(self, **kwargs):
        """
        Update an existing exam attempt (JWT required)
        """
        try:

            attempt_data = JWTAuth.authenticate_attempt()

            attempt_id = attempt_data['attempt_id']
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
    @http.route('/api/exams/attempts/delete/<int:attempt_id>', type='http', auth='public', methods=['DELETE'], csrf=False, cors="*")
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

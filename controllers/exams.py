# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessDenied, ValidationError
from .auth import JWTAuth
from ._helpers import _http_success_response, _http_error_response, _error_response, _success_response, _generate_code
import logging

_logger = logging.getLogger(__name__)

class ExamAPI(http.Controller):
    
    ## 🔹 [GET] Retrieve Exams by Course
    @http.route('/api/exams/get/<int:course_id>', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    def get_exams(self, course_id):
        """
        Retrieve exams filtered by course_id (JWT required)
        """
        try:
            user_data = JWTAuth.authenticate_request()
            user_id = user_data.get("user_id")

            # Filter exams by course_id if provided
            if not course_id:
                return _http_error_response('Course id is required')
            
            domain = [('course_id.user_ids', 'in', user_id), ('course_id', '=', int(course_id))]

            exams = request.env['easy_exams.exam'].sudo().search(domain)

            exam_data = [{
                'id': exam.id,
                'name': exam.name,
                'description': exam.description,
                'course_id': exam.course_id.id,
                'course_name': exam.course_id.name,
                'access_code': exam.access_code,
                'duration': exam.duration,
                'is_active': exam.is_active
            } for exam in exams]

            return _http_success_response(exam_data, "Exams retrieved successfully")
        except AccessDenied:
            return _http_error_response('Unauthorized: Access Denied', 401)
        except Exception as e:
            _logger.error(f"Error retrieving exams: {str(e)}")
            return _http_error_response(f"Error retrieving exams: {str(e)}", 500)

    ## 🔹 [POST] Create a New Exam
    @http.route('/api/exams/create', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def create_exam(self, **kwargs):
        """
        Create a new exam under an authorized course (JWT required)
        """
        try:
            user_data = JWTAuth.authenticate_request()
            user_id = user_data.get("user_id")

            name = kwargs.get('name')
            course_id = kwargs.get('course_id')
            duration = kwargs.get('duration', 45)  # Default duration is 45 mins

            if not name or not course_id:
                return _error_response('Missing required fields', 400)

            access_code = _generate_code(6)

            # Validate course ownership
            course = request.env['easy_exams.course'].sudo().search([('id', '=', course_id), ('user_ids', 'in', user_id)], limit=1)
            if not course:
                return _error_response("Unauthorized: You don't have access to this course", 403)

            new_exam = request.env['easy_exams.exam'].sudo().create({
                'name': name,
                'course_id': course.id,
                'description': kwargs.get('description', ''),
                'access_code': access_code,
                'duration': duration,
                'is_active': False,
            })

            return _success_response({'id': new_exam.id, 'name': new_exam.name}, "Exam created successfully")
        except ValidationError as e:
            return _error_response(str(e), 400)
        except AccessDenied:
            return _error_response('Unauthorized: Access Denied', 401)
        except Exception as e:
            _logger.error(f"Error creating exam: {str(e)}")
            return _error_response(f"Error creating exam: {str(e)}", 500)

    ## 🔹 [PUT] Update an Exam
    @http.route('/api/exams/update/', type='json', auth='public', methods=['PUT'], csrf=False, cors="*")
    def update_exam(self, **kwargs):
        """
        Update an existing exam (JWT required)
        """
        try:
            user_data = JWTAuth.authenticate_request()
            user_id = user_data.get("user_id")
            exam_id = kwargs.get('exam_id')
            if not exam_id:
                return _error_response('Exam id is required', 400)
            exam = request.env['easy_exams.exam'].sudo().search([('id', '=', exam_id), ('course_id.user_ids', 'in', user_id)], limit=1)
            if not exam:
                return _error_response("Exam not found or unauthorized", 400)

            update_data = {
                'name': kwargs.get('name', exam.name),
                'description': kwargs.get('description', exam.description),
                'duration': kwargs.get('duration', exam.duration),
                'is_active': kwargs.get('is_active', exam.is_active),
            }
            exam.sudo().write(update_data)

            return _success_response({'id': exam.id, 'name': exam.name}, "Exam updated successfully")
        except ValidationError as e:
            return _error_response(str(e), 400)
        except AccessDenied:
            return _error_response('Unauthorized: Access Denied', 401)
        except Exception as e:
            _logger.error(f"Error updating exam: {str(e)}")
            return _error_response(f"Error updating exam: {str(e)}", 500)

    ## 🔹 [PUT] Update an Exam
    @http.route('/api/exams/update_code', type='json', auth='public', methods=['PUT'], csrf=False, cors="*")
    def update_exam_code(self, **kwargs):
        """
        Update an existing exam (JWT required)
        """
        try:
            user_data = JWTAuth.authenticate_request()
            user_id = user_data.get("user_id")

            exam_id = kwargs.get('exam_id')
            if not exam_id:
                return _error_response('Exam id is required', 400)

            exam = request.env['easy_exams.exam'].sudo().search([('id', '=', exam_id), ('course_id.user_ids', 'in', user_id)], limit=1)
            if not exam:
                return _error_response("Exam not found or unauthorized", 404)
            access_code = _generate_code(6)
            update_data = {
                'access_code': access_code,
            }
            exam.sudo().write(update_data)

            return _success_response({'id': exam.id, 'name': exam.name, 'access_code': access_code}, "Exam updated successfully")
        except ValidationError as e:
            return _error_response(str(e), 400)
        except AccessDenied:
            return _error_response('Unauthorized: Access Denied', 401)
        except Exception as e:
            _logger.error(f"Error updating exam: {str(e)}")
            return _error_response(f"Error updating exam: {str(e)}", 500)

    ## 🔹 [PUT] Update an Exam
    @http.route('/api/exams/update_status', type='json', auth='public', methods=['PUT'], csrf=False, cors="*")
    def update_exam_status(self, **kwargs):
        """
        Update an existing exam (JWT required)
        """
        try:
            user_data = JWTAuth.authenticate_request()
            user_id = user_data.get("user_id")

            exam_id = kwargs.get('exam_id')
            if not exam_id:
                return _error_response('Exam id is required', 400)

            exam = request.env['easy_exams.exam'].sudo().search([('id', '=', exam_id), ('course_id.user_ids', 'in', user_id)], limit=1)
            if not exam:
                return _error_response("Exam not found or unauthorized", 404)

            update_data = {
                'is_active': not exam.is_active,
            }
            exam.sudo().write(update_data)

            return _success_response({'id': exam.id, 'name': exam.name, 'is_active': exam.is_active}, "Exam updated successfully")
        except ValidationError as e:
            return _error_response(str(e), 400)
        except AccessDenied:
            return _error_response('Unauthorized: Access Denied', 401)
        except Exception as e:
            _logger.error(f"Error updating exam: {str(e)}")
            return _error_response(f"Error updating exam: {str(e)}", 500)
        
    ## 🔹 [DELETE] Delete an Exam
    @http.route('/api/exams/delete/<int:exam_id>', type='http', auth='public', methods=['DELETE'], csrf=False, cors="*")
    def delete_exam(self, exam_id, **kwargs):
        """
        Delete an exam (JWT required)
        """
        try:
            user_data = JWTAuth.authenticate_request()
            user_id = user_data.get("user_id")

            exam = request.env['easy_exams.exam'].sudo().search([('id', '=', exam_id), ('course_id.user_ids', 'in', user_id)], limit=1)
            if not exam:
                return _http_error_response("Exam not found or unauthorized", 404)

            exam.sudo().unlink()

            return _http_success_response({'id': exam_id}, "Exam deleted successfully")
        except AccessDenied:
            return _http_error_response('Unauthorized: Access Denied', 401)
        except Exception as e:
            _logger.error(f"Error deleting exam: {str(e)}")
            return _http_error_response(f"Error deleting exam: {str(e)}", 500)

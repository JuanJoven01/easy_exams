# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessDenied
from .auth import JWTAuth
from ._helpers import _http_success_response, _http_error_response, _generate_code, _error_response, _success_response
import logging

_logger = logging.getLogger(__name__)

class CoursesAPI(http.Controller):
    ## 🔹 [GET] Retrieve Courses for Authenticated User
    @http.route('/api/exams/courses/get', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    def get_exams_courses(self, **kw):
        """
        Retrieves the courses that the authenticated user has access to.
        """
        try:
            user_data = JWTAuth.authenticate_request()  # Validate JWT
            user_id = user_data.get("user_id")

            # Get courses where the user is enrolled
            courses = request.env['easy_exams.course'].sudo().search([('user_ids', 'in', [user_id])])

            course_data = [{
                'id': course.id,
                'name': course.name,
                'description': course.description,
                'code': course.code,
                'access_key': course.access_key,
            } for course in courses]

            return _http_success_response(course_data, "Courses retrieved successfully.")
        
        except AccessDenied:
            return _http_error_response('Unauthorized: Access Denied', 401)
        except Exception as e:
            _logger.error(f"Error retrieving courses: {str(e)}")
            return _http_error_response(f"Error retrieving courses: {str(e)}", 500)

    ## 🔹 [POST] Create a New Course
    @http.route('/api/exams/courses/create', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def create_exam_course(self, **kwargs):
        """
        Creates a new course and assigns the authenticated user to it.
        """
        try:
            user_data = JWTAuth.authenticate_request()  # Validate JWT
            user_id = user_data.get("user_id")

            # Validate required data
            name = kwargs.get('name')
            if not name:
                return _error_response('Course name is required', 400)

            # Generate unique code and access key
            code = _generate_code(6)
            access_key = _generate_code(8)  # Could be hashed later

            # Create the course
            new_course = request.env['easy_exams.course'].sudo().create({
                'name': name,
                'description': kwargs.get('description', ''),
                'code': code,
                'access_key': access_key,  # Not encrypted for now
                'user_ids': [(4, user_id)],  # Assign first user
            })

            return _success_response({'course_id' : new_course.id}, "Course created successfully.")
        
        except AccessDenied:
            return _error_response('Unauthorized: Access Denied', 401)
        except Exception as e:
            _logger.error(f"Error creating course: {str(e)}")
            return _error_response(f"Error creating course: {str(e)}", 500)


    ## 🔹 [PUT] Update Course
    @http.route('/api/exams/courses/update/', type='json', auth='public', methods=['PUT'], csrf=False, cors="*")
    def update_exam_course(self, **kwargs):
        """
        Updates an existing course if the user has access.
        """
        try:
            user_data = JWTAuth.authenticate_request()  # Validate JWT
            user_id = user_data.get("user_id")

            course_id = kwargs.get("course_id")
            if not course_id:
                return _error_response('Course id is required', 400)
            # Find the course
            course = request.env['easy_exams.course'].sudo().search([
                ('id', '=', course_id),
                ('user_ids', 'in', [user_id])  # Ensure user has access
            ], limit=1)

            if not course:
                return _error_response("Course not found or access denied", 400)

            # Update fields if provided
            course.write({
                'name': kwargs.get('name', course.name),
                'description': kwargs.get('description', course.description),
            })

            # Prepare response
            updated_course = {
                'id': course.id,
                'name': course.name,
                'description': course.description,
                'code': course.code,
                'access_key': course.access_key,
            }

            return _success_response(updated_course, "Course updated successfully.")

        except AccessDenied:
            return _error_response("Unauthorized: Access Denied", 401)
        except Exception as e:
            _logger.error(f"Error updating course: {str(e)}")
            return _error_response(f"Error updating course: {str(e)}", 500)
        
    ## 🔹 [PUT] Add course to user
    @http.route('/api/exams/courses/update/add_user', type='json', auth='public', methods=['PUT'], csrf=False, cors="*")
    def add_user_to_course(self, **kwargs):
        """
        Updates an existing course if the user has access.
        """
        try:
            user_data = JWTAuth.authenticate_request()  # Validate JWT
            user_id = user_data.get("user_id")

            code = kwargs.get('code')
            access_key = kwargs.get('access_key')

            if not code or not access_key:
                return _error_response('Code and Access Key are required', 400)

            # Find the course
            course = request.env['easy_exams.course'].sudo().search([
                ('code', '=', code) # Ensure user has access
            ], limit=1)

            if not course:
                return _error_response("Course not found", 400)

            if access_key != course.access_key:
                return _error_response('Invalid Access Key', 403)

            # Add the user to the course
            if user_id not in course.user_ids.ids :
                course.write({'user_ids': [(4, user_id)]})

            # Prepare response
            updated_course = {
                'id': course.id,
                'name': course.name,
                'description': course.description,
                'code': course.code,
                'access_key': course.access_key,
            }

            return _success_response(updated_course, "Course updated successfully.")

        except AccessDenied:
            return _error_response("Unauthorized: Access Denied", 401)
        except Exception as e:
            _logger.error(f"Error updating course: {str(e)}")
            return _error_response(f"Error updating course: {str(e)}", 500)
        

    ## 🔹 [DELETE] Delete Course
    @http.route('/api/exams/courses/delete/<int:course_id>', type='http', auth='public', methods=['DELETE'], csrf=False, cors="*")
    def delete_exam_course(self, course_id, **kwargs):
        """
        Deletes a course if the user has access.
        """
        try:
            user_data = JWTAuth.authenticate_request()  # Validate JWT
            user_id = user_data.get("user_id")

            # Find the course
            course = request.env['easy_exams.course'].sudo().search([
                ('id', '=', course_id),
                ('user_ids', 'in', [user_id])  # Ensure user has access
            ], limit=1)

            if not course:
                return _http_error_response("Course not found or access denied", 400)

            # Delete course
            course.unlink()

            return _http_success_response({}, "Course deleted successfully.")

        except AccessDenied:
            return _http_error_response("Unauthorized: Access Denied", 401)
        except Exception as e:
            _logger.error(f"Error deleting course: {str(e)}")
            return _http_error_response(f"Error deleting course: {str(e)}", 500)
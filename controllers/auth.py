import jwt
import datetime
import logging
from odoo import http
from odoo.http import request, Response
from odoo.exceptions import AccessDenied

from ._helpers import _success_response, _error_response

_logger = logging.getLogger(__name__)

class JWTAuth:
    """Middleware for handling JWT authentication"""

    @staticmethod
    def get_secret_key():
        """Fetch secret key from Odoo system parameters"""
        return request.env['ir.config_parameter'].sudo().get_param('easy_apps_secret_key', 'default_secret')

    @staticmethod
    def generate_token(user):
        """Generate JWT token for authentication"""
        payload = {
            'user_id': user.id,
            'login': user.login,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
        }
        return jwt.encode(payload, JWTAuth.get_secret_key(), algorithm='HS256')

    @staticmethod
    def generate_attempt_token(payload : dict, expiration_time: int):
        """Generate JWT token for authentication while is takin exam """
        token_payload = {
            'student_id': payload['student_id'],
            'attempt_id': payload['attempt_id'] ,
            'exam_id': payload['exam_id'] ,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes= (expiration_time + 1) ) #  1 minute more for backend queries
            }
        return jwt.encode(token_payload, JWTAuth.get_secret_key(), algorithm='HS256')

    @staticmethod
    def decode_token(token):
        """Decode JWT token"""
        try:
            return jwt.decode(token, JWTAuth.get_secret_key(), algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AccessDenied("Expired Token")
        except jwt.InvalidTokenError:
            raise AccessDenied("Invalid Token")

    @staticmethod
    def authenticate_request():
        """Middleware to verify JWT token in protected endpoints"""
        token = request.httprequest.headers.get('Authorization')

        if not token:
            raise AccessDenied("Missing Authorization Header")

        if not token.startswith('Bearer '):
            raise AccessDenied("Invalid Token Format. Use 'Bearer <token>'")

        token = token.split(' ')[1]  # Extract actual token
        decoded_token = JWTAuth.decode_token(token)

        if not decoded_token:
            raise AccessDenied("Invalid or expired token")

        return decoded_token

    @staticmethod
    def authenticate_attempt():
        """Middleware to verify JWT token in protected endpoints"""
        token = request.httprequest.headers.get('Authorization')

        if not token:
            raise AccessDenied("Missing Authorization Header")

        if not token.startswith('Bearer '):
            raise AccessDenied("Invalid Token Format. Use 'Bearer <token>'")

        token = token.split(' ')[1]  # Extract actual token
        decoded_token = JWTAuth.decode_token(token)

        if not decoded_token:
            raise AccessDenied("Invalid or expired token")

        return decoded_token


class JWTAuthController(http.Controller):
    @http.route('/api/easy_apps/exams/auth', type='json', auth='public', methods=['POST'], csrf=False)
    def login(self, **kwargs):
        """
        Authenticate user and return JWT token.
        """
        try:
            login = kwargs.get('login')
            password = kwargs.get('password')

            if not login or not password:
                return _error_response("Missing login or password", 400)

            # Search for user in Odoo
            user = request.env['res.users'].sudo().search([('login', '=', login)], limit=1)
            db = request.db
            credential = { 'type': 'password', 'login': login, 'password': password }

            if not user:
                return _error_response("Invalid credentials", 403)
            
            user.sudo().authenticate(db, credential, {'interactive': True})
            easy_apps_group_id = request.env['ir.config_parameter'].sudo().get_param('easy_app_group_id') #gets the default groups id
            if not user.has_group(easy_apps_group_id):
                return _error_response("Unauthorized", 403)

            # Generate JWT token
            token = JWTAuth.generate_token(user)

            return _success_response({'token': token, 'user_id': user.id, 'login': user.login})
        except AccessDenied as e:
            return _error_response(str(e), 500)
        except Exception as e:
            _logger.error(str(e))
            return _error_response('Internal server error', 500)

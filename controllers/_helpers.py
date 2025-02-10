import json
from odoo.http import Response

def _http_success_response(data, message="Request successful", status=200):
    """
    Generate a standardized HTTP success response.
    :param data: The actual response data.
    :param message: A success message.
    :param status: HTTP status code (default 200).
    :return: HTTP JSON response.
    """
    return Response(json.dumps({
        'status': 'success',
        'message': message,
        'data': data
    }), content_type="application/json", status=status)


def _http_error_response(error_message, status=400):
    """
    Generate a standardized HTTP error response.
    :param error_message: The error message to display.
    :param status: The HTTP status code (default is 400).
    :return: HTTP JSON response.
    """
    return Response(json.dumps({
        'status': 'error',
        'message': error_message
    }), content_type="application/json", status=status)


def _success_response(data, message="Request successful"):
    """
    Generate a standardized success response.
    :param data: The actual response data.
    :param message: A success message.
    :return: JSON response.
    """
    return {
        'status': 'success',
        'message': message,
        'data': data
    }


def _error_response(error_message, status=400):
    """
    Generate a standardized error response.
    :param error_message: The error message to display.
    :param status: The HTTP status code (default is 400).
    :return: JSON response.
    """
    return {
        'status': 'error',
        'message': error_message,
        'code': status
    }

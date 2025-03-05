# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessDenied, ValidationError
from ._helpers import _http_success_response, _http_error_response, _error_response, _success_response
import logging
from .auth import JWTAuth

_logger = logging.getLogger(__name__)

class QuestionAnswerAPI(http.Controller):
    
    ## 🔹 [GET] Retrieve Answers by Attempt
    @http.route('/api/exams/answers/get/<int:attempt_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_answers(self, attempt_id, **kwargs):
        """
        Retrieve answers filtered by attempt_id.
        """
        try:
            JWTAuth.authenticate_request()

            if not attempt_id:
                return _error_response("Attempt ID is required", 400)

            # Find the attempt (to validate access)
            attempt = request.env['easy_exams.exam_attempt'].sudo().search([('id', '=', attempt_id)], limit=1)
            if not attempt:
                return _error_response("Attempt not found", 404)

            # Retrieve answers for the given attempt
            answers = request.env['easy_exams.question_answer'].sudo().search([('attempt_id', '=', attempt_id)])

            answer_data = [{
                'id': answer.id,
                'question': answer.question_id.read(['id', 'content', 'image','question_type'])[0],  # Ensure single dictionary output
                'options': [{'id': opt.id, 'content': opt.content, 'is_correct': opt.is_correct} for opt in answer.question_id.option_ids],
                'selected_options': [{'id': opt.id, 'question_option_id': opt.question_option.id} for opt in answer.selected_option_ids],
                'pair_options': [{'id': opt.id, 'term': opt.term, 'match': opt.match} for opt in answer.question_id.pair_ids],
                'pair_selected': [{'id': opt.id, 'question_pair_id': opt.question_pair_id, 'selected_match': opt.selected_match} for opt in answer.answer_pair_ids],
                'answer_text': answer.answer_text,
                'is_correct': answer.is_correct
            } for answer in answers]

            return _http_success_response(answer_data, "Answers retrieved successfully")
        
        except AccessDenied:
            return _http_error_response("Unauthorized: Access Denied", 401)
        
        except Exception as e:
            _logger.error(f"Error retrieving answers: {str(e)}")
            return _http_error_response(f"Error retrieving answers: {str(e)}", 500)
        
     ## 🔹 [GET] Retrieve Raw Answers by Attempt
    @http.route('/api/exams/raw_answers', type='http', auth='public', methods=['GET'], csrf=False)
    def get_raw_answers(self, **kwargs):
        """
        Retrieve war answers filtered by attempt_id while the student is taking the exam.
        """
        try:
            attempt_data = JWTAuth.authenticate_attempt()

            attempt_id = attempt_data['attempt_id']

            if not attempt_id:
                return _error_response("Attempt ID is required", 400)

            # Find the attempt (to validate access)
            attempt = request.env['easy_exams.exam_attempt'].sudo().search([('id', '=', attempt_id)], limit=1)
            if not attempt:
                return _error_response("Attempt not found", 404)

            # Retrieve answers for the given attempt
            answers = request.env['easy_exams.question_answer'].sudo().search([('attempt_id', '=', attempt_id)])
            print(answers.read())
            answer_data = [{
                'id': answer.id,
                'question_id': answer.question_id.id,
                'selected_options': [{'id': opt.id, 'question_option_id': opt.question_option.id} for opt in answer.selected_option_ids],
                'pair_selected': [{'id': opt.id, 'question_pair_id': opt.question_pair_id.id, 'selected_match': opt.selected_match} for opt in answer.answer_pair_ids],
                'answer_text': answer.answer_text,
            } for answer in answers]
            print(answers.read())
            return _http_success_response(answer_data, "Answers (cleaned) retrieved successfully")
        
        except AccessDenied:
            return _http_error_response("Unauthorized: Access Denied", 401)
        
        except Exception as e:
            _logger.error(f"Error retrieving answers: {str(e)}")
            return _http_error_response(f"Error retrieving answers: {str(e)}", 500)


    ## 🔹 [POST] Create a New Answer
    @http.route('/api/exams/answers/create', type='json', auth='public', methods=['POST'], csrf=False)
    def create_answer(self, **kwargs):
        """
        Create a new answer for a question.
        """
        try:
            attempt_data = JWTAuth.authenticate_attempt()
            attempt_id = attempt_data['attempt_id']

            question_id = kwargs.get('question_id')

            selected_options = kwargs.get('selected_options')
            selected_pairs = kwargs.get('selected_pairs')

            answer_text = kwargs.get('answer_text', '')

            if not attempt_id or not question_id:
                return _error_response("Attempt ID and Question ID are required", 400)

            answer_data = {
                'attempt_id': attempt_id,
                'question_id': question_id,
                'answer_text': answer_text,
            }

            new_answer = request.env['easy_exams.question_answer'].sudo().create(answer_data)
            
            if selected_options:
                [request.env['easy_exams.answer_option'].sudo().create({
                    'question_option' : selected_option,
                    'answer_id' : new_answer.id
                }) for selected_option in selected_options]

            selected_option_id = 0
            if new_answer.selected_option_ids:
                selected_option_id = new_answer.selected_option_ids[0].question_option.id

            if selected_pairs:
                [request.env['easy_exams.question_answer_pair'].sudo().create({
                    'answer_id' : new_answer.id,
                    'question_pair_id' : selected_pair['question_pair_id'],
                    'selected_match' : selected_pair['selected_match'],
                }) for selected_pair in selected_pairs]

            selected_pairs_return = []
            if new_answer.answer_pair_ids:
                for pair in new_answer.answer_pair_ids:
                    selected_pairs_return.append({
                        'question_pair_id': pair.question_pair_id.id,
                        'selected_match': pair.selected_match
                    })

            return _success_response({'id': new_answer.id, 'question_id':question_id, 'answer_text':  answer_text, 'selected_option_id': selected_option_id  , 'selected_pairs': selected_pairs_return }, "Answer recorded successfully")
        
        except AccessDenied:
            return _http_error_response("Unauthorized: Access Denied", 401)
        except ValidationError as e:
            return _error_response(str(e), 400)
        except Exception as e:
            _logger.error(f"Error creating answer: {str(e)}")
            return _error_response(f"Error creating answer: {str(e)}", 500)

    ## 🔹 [PUT] Update an Answer
    @http.route('/api/exams/answers/update', type='json', auth='public', methods=['PUT'], csrf=False)
    def update_answer(self, **kwargs):
        """
        Update an existing answer.
        """
        try:

            attempt_data = JWTAuth.authenticate_attempt()

            attempt_id = attempt_data['attempt_id']

            answer_id = kwargs.get('answer_id') 
            selected_options = kwargs.get('selected_options') #receives an list of ids
            selected_pairs = kwargs.get('selected_pairs')
            if not answer_id:
                return _error_response('Answer id is required', 400)
            
            answer = request.env['easy_exams.question_answer'].sudo().browse(answer_id)
            if not answer.exists():
                return _error_response("Answer not found", 404)
            
            if selected_options:

                answer.selected_option_ids.unlink()

                new_options = [
                    (0, 0, 
                    {
                        'question_option': selected_option, 
                        'answer_id': answer.id
                    })
                    for selected_option in selected_options]
                answer.write({'selected_option_ids': new_options})
            
            
            if selected_pairs:

                answer.answer_pair_ids.unlink()

                new_pairs = [
                    (0, 0, 
                    {
                        'answer_id': answer.id,
                        'question_pair_id': selected_pair['question_pair_id'],
                        'selected_match': selected_pair['selected_match']
                    })
                    for selected_pair in selected_pairs]

                answer.write({'answer_pair_ids': new_pairs})

            update_data = {
                'answer_text': kwargs.get('answer_text', answer.answer_text),
            }
            answer.sudo().write(update_data)

            return _success_response({'id': answer.id}, "Answer updated successfully")

        except AccessDenied:
            return _http_error_response("Unauthorized: Access Denied", 401)
        except Exception as e:
            _logger.error(f"Error updating answer: {str(e)}")
            return _error_response(f"Error updating answer: {str(e)}", 500)

    ## 🔹 [DELETE] Delete an Answer
    @http.route('/api/exams/answers/delete/<int:answer_id>', type='http', auth='public', methods=['DELETE'], csrf=False)
    def delete_answer(self, answer_id, **kwargs):
        """
        Delete an answer.
        """
        try:
            JWTAuth.authenticate_request()
            answer = request.env['easy_exams.question_answer'].sudo().browse(answer_id)

            if not answer.exists():
                return _error_response("Answer not found", 404)

            answer.sudo().unlink()

            return _http_success_response({'id': answer_id}, "Answer deleted successfully")
        except Exception as e:
            _logger.error(f"Error deleting answer: {str(e)}")
            return _http_error_response(f"Error deleting answer: {str(e)}", 500)

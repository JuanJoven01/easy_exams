from odoo import models, fields, api
from openai import OpenAI
import re
import json

def _use_deepSeek(self, sys_message, user_message):
    try:
        _api_key = self.env['ir.config_parameter'].sudo().get_param('exams_deep_seek')
        client = OpenAI(api_key=_api_key, base_url="https://api.deepseek.com")

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": sys_message},
                {"role": "user", "content": user_message},
            ],
            stream=False
        )
        return response.choices[0].message.content
    except:
        return '2'
    
class QuestionAnswer(models.Model):
    _name = 'easy_exams.question_answer'
    _description = 'Question Answer'

    attempt_id = fields.Many2one('easy_exams.exam_attempt', string="Exam Attempt", required=True , ondelete="cascade")
    question_id = fields.Many2one('easy_exams.question', string="Question", required=True, ondelete="cascade")
    selected_option_ids = fields.One2many('easy_exams.answer_option', 'answer_id',  string="Selected Options")
    answer_text = fields.Text(string="Answer Text")
    is_correct = fields.Boolean(string="Is Correct")
    q_score = fields.Float(string="Score between 0 and 1", default=2)
    answer_pair_ids = fields.One2many('easy_exams.question_answer_pair', 'answer_id', string="Answer Pairs")


    @api.model_create_multi
    def create(self, vals_list):
        records = super(QuestionAnswer, self).create(vals_list)
        for record in records:
            self._qualify_answer(record)
        return records

    def _qualify_answer(self, record):
        """
        
        """
        try:
            if record.question_id.question_type == 'matching':
                if not record.answer_pair_ids:
                    record.sudo().write({
                        'is_correct': False,
                        'q_score': 0
                    })
                else:
                    ok = 0
                    bad = 0
                    for selected_pair in record.answer_pair_ids:
                        if selected_pair.selected_match == selected_pair.question_pair_id.match:
                            ok += 1
                        else: 
                            bad += 1
                    score = 0
                    if ok + bad != 0:
                        score = ok / (ok + bad)
                    is_correct = False
                    if score >= 0.6:
                        is_correct = True
                    
                    record.sudo().write({
                        'is_correct': is_correct,
                        'q_score': score
                    })
            if record.question_id.question_type == 'fill_in_the_blank':
                regex = r'\{\{(\d+)\}\}'
                expected_answers = re.findall(regex, record.question_id.correct_answer)
                expected_answers = str(expected_answers) #ensure is a list
                raw_answers = json.loads(record.answer_text)
                answers = [raw_answer['value'] for raw_answer in raw_answers]
                answers = str(answers)
                score = 0
                is_correct = False
                api_response = _use_deepSeek(
                    self,
                    """
                    You will help me automatically grade fill in the blank exams. To do this, I will provide you with the following information:
                    Answer order: I will specify whether the answers should be ordered or unordered.
                    Ideal answers list: A list of the correct expected answers.
                    User answers list: A list of the answers provided by the user.
                    Your task is to compare the user's answers with the ideal answers, considering the following:
                    The answers may contain grammatical errors but must be understandable.
                    The answers may be in another language but must mean the same as the ideal answers.
                    If the answers should be ordered, the position of each answer matters. If they should be unordered, only the content matters, not the order.
                    Finally, you must calculate a score as a float between 0 and 1, where:
                    0 means all answers are incorrect.
                    1 means all answers are correct.
                    Your response must be only the float, without any additional explanations, as my Python code will take your response and store it in a database as a float value.
                    """,
                    f'{str(record.question_id.correct_answer)} {expected_answers} {answers}'
                )
                print('api response fill in the blank ')
                print(api_response)
                if score >= 0.6:
                    is_correct = True
                record.sudo().write({
                    'is_correct': is_correct,
                    'q_score': score
                })
            if record.question_id.question_type == 'short_answer' or record.question_id.question_type == 'long_answer':
                score = 0
                is_correct = False
                api_response = _use_deepSeek(
                    self,
                    """
                    You will help me automatically grade short or long answer questions. For this, I will provide you with the following:
                    Expected answer: The correct answer or a description of what the answer should include. This may also contain additional instructions about the expected response (e.g., specific details, format, or key points).
                    Submitted answer: The answer provided by the user.
                    Your task is to compare the submitted answer with the expected answer, considering the following:
                    The submitted answer may contain grammatical errors but must be understandable.
                    The submitted answer may be in another language but must convey the same meaning as the expected answer.
                    If the expected answer includes additional instructions (e.g., specific details or format), you must evaluate whether the submitted answer meets those requirements.
                    Finally, you must calculate a score as a float between 0 and 1, where:
                    0 means the answer is completely incorrect or does not meet the requirements.
                    1 means the answer is fully correct and meets all requirements.
                    Your response must be only the float, without any additional explanations, as my Python code will take your response and store it in a database as a float value.
                    """,
                    f'Expected answer: {str(record.question_id.correct_answer)} Submitted answer: {str(record.answer_text)}'
                )
                print('api response text ')
                print(score)
                if score >= 0.6:
                    is_correct = True
                record.sudo().write({
                    'is_correct': is_correct,
                    'q_score': score
                })
        except:
            record.sudo().write({
                    'is_correct': False,
                    'q_score': 2
                })
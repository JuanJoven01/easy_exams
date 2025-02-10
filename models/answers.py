from odoo import models, fields

class QuestionAnswer(models.Model):
    _name = 'easy_exams.question_answer'
    _description = 'Question Answer'

    attempt_id = fields.Many2one('easy_exams.exam_attempt', string="Exam Attempt", required=True)
    question_id = fields.Many2one('easy_exams.question', string="Question", required=True)
    selected_option_ids = fields.Many2many('easy_exams.question_option', string="Selected Options")
    answer_text = fields.Text(string="Answer Text")
    is_correct = fields.Boolean(string="Is Correct")
    answer_pair_ids = fields.One2many('easy_exams.question_answer_pair', 'question_answer_id', string="Answer Pairs")

from odoo import models, fields

class QuestionAnswer(models.Model):
    _name = 'easy_exams.question_answer'
    _description = 'Question Answer'

    attempt_id = fields.Many2one('easy_exams.exam_attempt', string="Exam Attempt", required=True , ondelete="cascade")
    question_id = fields.Many2one('easy_exams.question', string="Question", required=True, ondelete="cascade")
    selected_option_ids = fields.One2many('easy_exams.answer_option', 'answer_id',  string="Selected Options")
    answer_text = fields.Text(string="Answer Text")
    is_correct = fields.Boolean(string="Is Correct")
    q_score = fields.Float(string="Score between 0 and 1")
    answer_pair_ids = fields.One2many('easy_exams.question_answer_pair', 'answer_id', string="Answer Pairs")

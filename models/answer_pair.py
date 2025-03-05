from odoo import models, fields

class QuestionAnswerPair(models.Model):
    _name = 'easy_exams.question_answer_pair'
    _description = 'Question Answer Pair'

    answer_id = fields.Many2one('easy_exams.question_answer', string="Question Answer", required=True, ondelete='cascade')
    question_pair_id = fields.Many2one('easy_exams.question_pair', string="Question Pair", required=True, ondelete='cascade')
    selected_match = fields.Char(string="Selected Match", required=True)

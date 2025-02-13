from odoo import models, fields

class AnswerOption(models.Model):
    _name = 'easy_exams.answer_option'
    _description = 'Answer Option'

    answer_id = fields.Many2one('easy_exams.question_answer', string="Question Answer", required=True)
    question_option = fields.Many2one('easy_exams.question_option', string="Options", required=True)

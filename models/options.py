from odoo import models, fields

class QuestionOption(models.Model):
    _name = 'easy_exams.question_option'
    _description = 'Question Option'

    question_id = fields.Many2one('easy_exams.question', string="Question", required=True, ondelete='cascade')
    content = fields.Char(string="Option Content", required=True)
    is_correct = fields.Boolean(string="Is Correct", default=False)

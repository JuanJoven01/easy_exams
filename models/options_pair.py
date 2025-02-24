from odoo import models, fields

class QuestionPair(models.Model):
    _name = 'easy_exams.question_pair'
    _description = 'Question Pair'

    question_id = fields.Many2one('easy_exams.question', string="Question", required=True, ondelete="cascade")
    term = fields.Char(string="Term", required=True)
    match = fields.Char(string="Match", required=True)

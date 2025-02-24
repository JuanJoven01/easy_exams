from odoo import models, fields

class Question(models.Model):
    _name = 'easy_exams.question'
    _description = 'Question'

    exam_id = fields.Many2one('easy_exams.exam', string="Exam", required=True,ondelete='cascade')
    question_type = fields.Selection([
        ('multiple_choice', 'Multiple Choice'),
        ('fill_in_the_blank', 'Fill in the Blank'),
        ('short_answer', 'Short Answer'),
        ('long_answer', 'Long Answer'),
        ('matching', 'Matching')
    ], string="Question Type", required=True)
    content = fields.Text(string="Content", required=True)
    image = fields.Image(string="Image") 
    option_ids = fields.One2many('easy_exams.question_option', 'question_id', string="Options")
    pair_ids = fields.One2many('easy_exams.question_pair', 'question_id', string="Pairs")
    correct_answer = fields.Text(string="Correct Answer")

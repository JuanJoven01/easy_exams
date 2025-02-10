from odoo import models, fields

class Exam(models.Model):
    _name = 'easy_exams.exam'
    _description = 'Exam'

    name = fields.Char(string="Exam Title", required=True)
    course_id = fields.Many2one('easy_exams.course', string="Course", required=True)
    description = fields.Text(string="Description")
    question_ids = fields.One2many('easy_exams.question', 'exam_id', string="Questions")
    access_code = fields.Char(string="Access Code", required=True)
    duration = fields.Integer(string="Duration (minutes)")
    is_active = fields.Boolean(string='Is the exam active to responses?', required=True, default= False)

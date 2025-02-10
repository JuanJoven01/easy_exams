from odoo import models, fields

class ExamAttempt(models.Model):
    _name = 'easy_exams.exam_attempt'
    _description = 'Exam Attempt'

    exam_id = fields.Many2one('easy_exams.exam', string="Exam", required=True)
    student_name = fields.Char(string="Student Name", required=True)
    student_id = fields.Char(string="Student ID", required=True)
    start_time = fields.Datetime(string="Start Time", default=fields.Datetime.now)
    end_time = fields.Datetime(string="End Time")
    score = fields.Float(string="Score")
    answer_ids = fields.One2many('easy_exams.question_answer', 'attempt_id', string="Answers")
    

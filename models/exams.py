from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Exam(models.Model):
    _name = 'easy_exams.exam'
    _description = 'Exam'

    name = fields.Char(string="Exam Title", required=True)
    course_id = fields.Many2one('easy_exams.course', string="Course", required=True, ondelete="cascade")
    description = fields.Text(string="Description")
    question_ids = fields.One2many('easy_exams.question', 'exam_id', string="Questions", order='id asc')
    access_code = fields.Char(string="Access Code", required=True)
    duration = fields.Integer(string="Duration (minutes)")
    is_active = fields.Boolean(string='Is the exam active to responses?', required=True, default= False)
    
    @api.constrains('duration')
    def _check_duration(self):
        """Ensure exam duration is positive."""
        for exam in self:
            if exam.duration <= 0:
                raise ValidationError("Exam duration must be greater than zero.")
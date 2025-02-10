from odoo import models, fields
class Course(models.Model):
    _name = 'easy_exams.course'
    _description = 'Course'

    name = fields.Char(string="Course Name", required=True)
    description = fields.Text(string="Description")
    code = fields.Char(string="Course Code", required=True, unique=True)
    access_key = fields.Char(string="Access Key", required=True)
    exam_ids = fields.One2many('easy_exams.exam', 'course_id', string="Exams")
    user_ids = fields.Many2many('res.users', string="Authorized Users")
    
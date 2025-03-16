from odoo import models, fields, api

class AnswerOption(models.Model):
    _name = 'easy_exams.answer_option'
    _description = 'Answer Option'

    answer_id = fields.Many2one('easy_exams.question_answer', string="Question Answer", required=True, ondelete='cascade' )
    question_option = fields.Many2one('easy_exams.question_option', string="Options", required=True, ondelete='cascade')

    @api.model_create_multi
    def create(self, vals_list):
        records = super(AnswerOption, self).create(vals_list)
        for record in records:
            self._qualify_answer(record)
        return records

    def _qualify_answer(self, record):
        """
        
        """
        try:
            if record.question_option.is_correct:
                question = self.env['easy_exams.question_answer'].sudo().search([('id', '=', record.answer_id.id)], limit=1)
                question.sudo().write({
                    'is_correct': True,
                    'q_score': 1
                })
            else:
                question = self.env['easy_exams.question_answer'].sudo().search([('id', '=', record.answer_id.id)], limit=1)
                question.sudo().write({
                    'is_correct': False,
                    'q_score': 0
                })
        except:
            question = self.env['easy_exams.question_answer'].sudo().search([('id', '=', record.answer_id.id)], limit=1)
            question.sudo().write({
                'is_correct': False,
                'q_score': 2
            })
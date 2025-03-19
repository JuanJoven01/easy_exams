from odoo import models, fields, api

class QuestionAnswerPair(models.Model):
    _name = 'easy_exams.question_answer_pair'
    _description = 'Question Answer Pair'

    answer_id = fields.Many2one('easy_exams.question_answer', string="Question Answer", required=True, ondelete='cascade')
    question_pair_id = fields.Many2one('easy_exams.question_pair', string="Question Pair", required=True, ondelete='cascade')
    selected_match = fields.Char(string="Selected Match", required=True)

    @api.model_create_multi
    def create(self, vals_list):
        records = super(QuestionAnswerPair, self).create(vals_list)
        for record in records:
            self._qualify_answer(record)
        return records
    
    def write(self, vals):
        if not self.env.context.get('qualifying'): 
            self = self.with_context(qualifying=True)  
            result = super(QuestionAnswerPair, self).write(vals)
            for record in self:
                self._qualify_answer(record)
        else:
            result = super(QuestionAnswerPair, self).write(vals)
        return result
    
    def _qualify_answer(self, record):
        """
        
        """
        try:
            if record.selected_match == record.question_pair_id.match:
                number_of_matches = len(record.answer_id.question_id.pair_ids)
                answer = self.env['easy_exams.question_answer'].sudo().search([('id', '=', record.answer_id.id)], limit=1)
                old_score = answer.q_score
                if old_score == 2:
                    old_score = 0
                new_score = old_score + (1/number_of_matches)
                is_correct = False 
                if new_score >= 0.6:
                    is_correct: True
                answer.sudo().write({
                    'is_correct': is_correct,
                    'q_score': new_score
                })
        except:
            answer = self.env['easy_exams.question_answer'].sudo().search([('id', '=', record.answer_id.id)], limit=1)
            answer.sudo().write({
                    'is_correct': False,
                    'q_score': 2
                })
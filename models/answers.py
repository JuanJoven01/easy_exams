from odoo import models, fields, api

class QuestionAnswer(models.Model):
    _name = 'easy_exams.question_answer'
    _description = 'Question Answer'

    attempt_id = fields.Many2one('easy_exams.exam_attempt', string="Exam Attempt", required=True , ondelete="cascade")
    question_id = fields.Many2one('easy_exams.question', string="Question", required=True, ondelete="cascade")
    selected_option_ids = fields.One2many('easy_exams.answer_option', 'answer_id',  string="Selected Options")
    answer_text = fields.Text(string="Answer Text")
    is_correct = fields.Boolean(string="Is Correct")
    q_score = fields.Float(string="Score between 0 and 1", default=2)
    answer_pair_ids = fields.One2many('easy_exams.question_answer_pair', 'answer_id', string="Answer Pairs")

    @api.model_create_single
    def create(self, vals):
        """
        
        """
        record = super(QuestionAnswer, self).create(vals)
        self._qualify_answer(record)
        return record

    def _qualify_answer(self, record):
        """
        
        """
        if record.question_id.question_type == 'multiple_choice':
            if not record.selected_option_ids:
                record.sudo().write({
                    'is_correct': False,
                    'q_score': 0
                })
            else:
                all_options_correct = all(
                    option.question_option.is_correct
                    for option in record.selected_option_ids
                )
                if all_options_correct:
                    record.sudo().write({
                        'is_correct': True,
                        'q_score': 1
                    })
                else:
                    record.sudo().write({
                        'is_correct': False,
                        'q_score': 0
                    })
        if record.question_id.question_type == 'matching':
            if not record.answer_pair_ids:
                record.sudo().write({
                    'is_correct': False,
                    'q_score': 0
                })
            else:
                ok = 0
                bad = 0
                for selected_pair in record.answer_pair_ids:
                    if selected_pair.selected_match == selected_pair.question_pair_id.match:
                        ok += 1
                    else: 
                        bad += 1
                score = 0
                if ok + bad != 0:
                    score = ok / (ok + bad)
                is_correct = False
                if score >= 0.6:
                    is_correct = True
                
                record.sudo().write({
                    'is_correct': is_correct,
                    'q_score': score
                })
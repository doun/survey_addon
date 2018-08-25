from odoo import fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    survey_input_count = fields.Integer(compute = '_compute_survey_input_count', string='# of Answers')
    survey_input_ids = fields.One2many('survey.user_input', 'partner_id', 'User Answers')

    #action_show_user_input = fields

    def _compute_survey_input_count(self):
        user_answers = self.env['survey.user_input'].read_group(domain=[('partner_id', 'child_of', self.ids)], 
                                fields=['partner_id'], groupby=['partner_id'])
        child_ids = self.read(['child_ids'])
        mapped_data = dict([m['partner_id'][0], m['partner_id_count']] for m in user_answers)
        for p in self:
            item = next(pp for pp in child_ids if pp['id'] == p.id)
            p_ids = [p.id] + item.get('child_ids')
            p.survey_input_count = sum(mapped_data.get(child, 0) for child in p_ids)

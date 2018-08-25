# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime
import logging
import re
import base64
import uuid
from collections import Counter, OrderedDict
from itertools import product
from werkzeug import urls

from odoo import api, fields, models, tools, SUPERUSER_ID, _
#from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import UserError, ValidationError
_logger = logging.getLogger(__name__)


class SurveyQuestion(models.Model):
    _inherit = "survey.question"
    type = fields.Selection(selection_add=[('attach', '附件')])
    image_only = fields.Boolean('仅图片')
    file_name = fields.Char('保存文件名')

    @api.multi
    def validate_attach(self, post, answer_tag):
        self.ensure_one()
        errors = {}
        answer = post[answer_tag].strip()
        removed = post[answer_tag +'_removed'].strip()
        # Empty answer to mandatory question
        if self.constr_mandatory and removed == 'true':
            errors.update({answer_tag: self.constr_error_msg})

        return errors

class SurveyInputLine(models.Model):
    _inherit = 'survey.user_input_line'
    answer_type = fields.Selection(selection_add=[('attach', '附件')])

    @api.model
    def save_line_attach(self, user_input_id, question, post, answer_tag):
        Attach = self.env['ir.attachment']
        vals = {
            'user_input_id': user_input_id,
            'question_id': question.id,
            'survey_id': question.survey_id.id,
            'answer_type': 'number'
        }

        old_uil = self.search([
            ('user_input_id', '=', user_input_id),
            ('survey_id', '=', question.survey_id.id),
            ('question_id', '=', question.id)
        ])

        if not old_uil:
            old_uil.create(vals)

        # 删除
        if answer_tag + "_removed" in post:
            if post[answer_tag + "_removed"] == 'true':
                vals.update({'skipped': True, 'value_number': 0})
                if old_uil.value_number > 0:
                    Attach.browse([int(old_uil.value_number)]).unlink()
                old_uil.write(vals)
                return True

        if answer_tag in post:
            file = post[answer_tag]
            if file:
                content = file.stream.getvalue()
                vals.update({'skipped': False})
                # 替换文件内容
                if old_uil.value_number > 0:
                    att = Attach.browse([int(old_uil.value_number)])
                    att.write({'datas': base64.b64decode(content)})
                    #vals.update({'value_number': att.id}) 重用这条记录，只是更新内容
                    old_uil.write(vals)
                else:
                #新增文件
                    att = {
                        'name': question.file_name,
                        'datas_fname': question.file_name,
                        'res_model': 'survey.user_input',
                        'datas': base64.b64encode(content),
                        'res_field': question.id,
                        'res_id': user_input_id
                    }
                    att = Attach.create(att)
                    vals.update({'value_number': att.id, 'skipped': False})
                    old_uil.write(vals)
        return True


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'
    survey_id = fields.Many2one('survey.survey', readonly=False)
    partner_id = fields.Many2one('res.partner', readonly=False)
    type = fields.Selection(readonly=False)
    email = fields.Char(readonly=False)

    @api.multi
    def action_open_url(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': '/survey/fill/%s/%s' % (self.survey_id.id, self.token)
        }

# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import csv
import datetime
import logging
import re
import base64
import uuid
from collections import Counter, OrderedDict
from itertools import product
from werkzeug import urls

from odoo import api, fields, models, tools, SUPERUSER_ID, _
# from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import UserError, ValidationError
_logger = logging.getLogger(__name__)


class SurveyQuestion(models.Model):
    _inherit = "survey.question"
    type = fields.Selection(selection_add=[('attach', '附件')])
    image_only = fields.Boolean('仅图片')
    file_ext = fields.Char('文件类型')
    file_name = fields.Char('保存文件名')

    @api.multi
    def validate_attach(self, post, answer_tag):
        self.ensure_one()
        errors = {}
        file_tag = 'file_' + answer_tag
        has_data = False
        if answer_tag in post and post[answer_tag] != 'remove':
            has_data = True
        if file_tag in post and post[file_tag]:
            has_data = True
        if self.constr_mandatory and not has_data:
            errors.update({answer_tag: self.constr_error_msg})

        return errors


class SurveyInputLine(models.Model):
    _inherit = 'survey.user_input_line'
    answer_type = fields.Selection(selection_add=[('attach', '附件')])

    @api.model
    def save_line_attach(self, user_input_id, question, post, answer_tag):
        Attach = self.env['ir.attachment']
        file_tag = "file_" + answer_tag
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

        # 删除
        if (answer_tag in post and post[answer_tag] == 'remove') or answer_tag not in post:
            vals.update({'value_number': ''})
            if old_uil and old_uil.value_number:
                Attach.browse([int(old_uil.value_number)]).sudo().unlink()
                old_uil.write(vals)
            return True
        else:
            if file_tag in post:
                file = post[file_tag]
                if file:
                    content = file.read()
                    vals.update({'skipped': False})
                    # 替换文件内容
                    if old_uil and old_uil.value_number:
                        att = Attach.browse([int(old_uil.value_number)])
                        att.write({'datas': base64.b64decode(content)})
                    else:
                        # 新增文件
                        att = {
                            'name': question.file_name,
                            'datas_fname': question.file_name,
                            'res_model': 'survey.user_input',
                            'datas': base64.b64encode(content),
                            # 'res_field': question.id,
                            'res_id': user_input_id
                        }
                        att = Attach.create(att)
                        vals.update(
                            {'value_number': str(att.id), 'skipped': False})

        if old_uil:
            old_uil.write(vals)
        else:
            old_uil.create(vals)
        return True


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'
    survey_id = fields.Many2one('survey.survey', readonly=False)
    partner_id = fields.Many2one('res.partner', readonly=False)
    task_id = fields.Many2one('project.task', string='附加到任务')
    state = fields.Selection(readonly=False)
    type = fields.Selection(readonly=False)
    email = fields.Char(readonly=False)

    def to_csv_line(self, line):
        title = line.question_id.question
        val = ""
        if 'text' in str(line.answer_type):
            val = line.value_text
        if line.answer_type == 'date':
            val = str(line.value_date)
        if line.answer_type == 'suggestion':
            val = line.question_id.label_ids[line.value_suggested_row].value
        if line.answer_type == 'number':
            val = string(line.value_number)
        return (title, val)


    @api.multi
    def pack_as_attach(self):
        self.ensure_one()
        Attach = self.env['ir.attachment']
        # TODO: Step1. Gen csv from inputs
        csv_f = csv.StringIO()
        csv_w = csv.DictWriter(csv_f, ['title', 'value'])
        lines = [self.to_csv_line(l) for l in self.user_input_line_ids if l.question_id.type != 'attach' and l.skipped = False]
        for t, v in lines:
            csv_w.writerow({'title': t, 'value': v})

        att = {
            'name': self.question_id.file_name,
            'datas_fname': self.question_id.file_name,
            'res_model': 'survey.user_input',
            'datas': base64.b64encode(content),
            # 'res_field': question.id,
            'res_id': user_input_id
        }
        csv_att = Attach.create(att)

        # Step2. Gen zip
        return

    @api.multi
    def action_sendto_provider(self):
        return

    @api.multi
    def action_open_url(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': '/survey/fill/%s/%s' % (self.survey_id.id, self.token)
        }

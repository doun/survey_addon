# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Survey add on(attach question type, start from res_partner)',
    'version': '1.0',
    'category': 'Marketing',
    'description': """
    add attach question type for survey, allow survey to be started from res_partner, show their answers.
    """,
    'summary': 'survey addon',
    'website': 'https://github.com/doun',
    'depends': ['survey','contacts'],
    'data': [
        #'security/survey_security.xml',
        #'security/ir.model.access.csv',
        'views/survey_views.xml',
        'views/survey_templates.xml',
        'views/res_partner_views.xml',
        #'views/survey_result.xml',
        #'wizard/survey_email_compose_message.xml',
        #'data/survey_stages.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

# -*- coding: utf-8 -*-
{
    'name': "Payment Approve Access",
    'summary': """
        summary
    """,
    'description': """
        description
    """,
    'author': "Ragab",
    'contributors': [
        'Ragab Deaf <ragabdeaf93@outlook.com>',
    ],
    'version': '17.0',
    'depends': ['base', 'account'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/payment_approve_request.xml',
        'data/data.xml',
        'security/ir_rule.xml'
    ],
    'license': 'OPL-1',
    "pre_init_hook": None,
    "post_init_hook": None,
}
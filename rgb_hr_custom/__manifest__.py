# -*- coding: utf-8 -*-
{
    'name': "HR Custom",
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
    'version': '16.0',
    'depends': ['hr'],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_employee_views.xml",
    ],
    'license': 'OPL-1',
    "pre_init_hook": None,
    "post_init_hook": None,
}
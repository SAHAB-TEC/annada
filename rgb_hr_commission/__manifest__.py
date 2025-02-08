# -*- coding: utf-8 -*-
{
    'name': "HR Commissions",
    'summary': """
        HR Commissions
    """,
    'description': """
        HR Commissions
    """,
    'author': "Ragab",
    'contributors': [
        'Ragab Deaf <ragabdeaf93@outlook.com>',
    ],
    'version': '17.0',
    'depends': ['hr', 'sale', 'sale_order_validity'],
    "data": [
        "security/ir.model.access.csv",
        'views/hr_employee_views.xml',
        'views/monthly_commission.xml',
        'views/uom.xml'
    ],
    'license': 'OPL-1',
    "pre_init_hook": None,
    "post_init_hook": None,
}
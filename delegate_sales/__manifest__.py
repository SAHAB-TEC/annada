# -*- coding: utf-8 -*-

{
    "name": "Delegate Sales",
    "version": "17.0.0.1",
    "category": "",
    'summary': 'Delegate Sales ',
    "author": "Ahmed Amen",
    "depends": ['base', 'sale', 'hr', 'hr_payroll_account', 'account', 'mrp'],
    "data": [
        'security/ir.model.access.csv',
        'view/delegate_validity_view.xml',
        'view/tmp.xml',
        'view/mrp.xml'
    ],
    "auto_install": False,
    "installable": True,

}

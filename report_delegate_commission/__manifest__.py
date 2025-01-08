# -*- coding: utf-8 -*-

{
    "name": "Delegate Commission",
    "version": "17.0.0.1",
    "category": "Delegate Commission",
    'summary': 'Delegate Commission',
    "author": "Ahmed Amen",
    "depends": ['base', 'hr','sale'],
    "data": [
        'security/ir.model.access.csv',
        'report/report_delegate_commission.xml',
        'report/tem_delegate_commission.xml',
        'wizard/delegate_commission_wizard_view.xml',
        'view/menu.xml',
    ],
    "auto_install": False,
    "installable": True,

}

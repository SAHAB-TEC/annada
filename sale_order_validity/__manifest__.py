# -*- coding: utf-8 -*-

{
    "name": "Sale Order Validity ",
    "version": "17.0.0.1",
    "category": "",
    'summary': 'Sale Order Validity ',
    "author": "Ahmed Amen",
    "depends": ['base', 'sale', 'purchase', 'hr', 'account', 'stock', 'product_expiry', 'delegate_sales'],
    "data": [
        'data/ir_sequence_data.xml',
        'view/sale_validity_view.xml',
        'security/groups.xml'
    ],
    "auto_install": False,
    "installable": True,

}

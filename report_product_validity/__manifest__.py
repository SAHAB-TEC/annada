# -*- coding: utf-8 -*-

{
    "name": "Product Validity",
    "version": "17.0.0.1",
    "category": "Product",
    'summary': 'Product Validity',
    "author": "Ahmed Amen",
    "depends": ['base', 'stock','product_expiry'],
    "data": [
        'security/ir.model.access.csv',
        'report/report_product_validity.xml',
        'report/tem_product_validity.xml',
        'wizard/product_validity_wizard_view.xml',
        'view/menu.xml',
    ],
    "auto_install": False,
    "installable": True,

}

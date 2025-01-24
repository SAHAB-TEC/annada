{
    'name': 'MRP Bill of Material Details',
    'version': '1.0',
    'summary': 'Generate Bill of Material Details Report',
    'author': 'Marwah Adel',
    'depends': ['base', 'product', 'stock','mrp','BOM_details_report'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard_views.xml',
        'views/bill_of_material_menu.xml',
        'reports/bill_of_material_report.xml',
    ],
    'application': False,
    'installable': True,
}

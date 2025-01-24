{
    'name': 'Bill of Material Details',
    'version': '1.0',
    'summary': 'Generate Bill of Material Details Report',
    'author': 'Marwah Adel',
    'depends': ['base', 'product', 'stock','mrp', 'purchase', 'product_annual_target', 'product_multi_uom'],
    "data": [
        "security/group.xml",
        "security/ir.model.access.csv",
        "wizard/wizard_views.xml",
        "views/bill_of_material_menu.xml",
        "reports/bill_of_material_report.xml",
        "views/bom_details_reports_views.xml"
    ],
    'application': False,
    'installable': True,
}

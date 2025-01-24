{
    'name': 'Average Sales Report',
    'version': '17.0',
    'summary': 'Generate an Average Sales Report based on inventory data',
    'category': 'Inventory',
    'author': 'marwah adel',
    'depends': ['stock', 'base' ,'BOM_details_report'],
    "data": [
        "security/ir.model.access.csv",
        "views/average_sales_report_menu.xml",
        "reports/average_sales_report_template.xml",
        "views/product_year_target_views.xml",
        'reports/product_target_year_report.xml',
    ],
    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}

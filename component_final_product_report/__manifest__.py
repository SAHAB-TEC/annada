{
    'name': 'Component of Final Product Report',
    'version': '17.0',
    'category': 'Inventory',
    'summary': 'Generate a report of final products using a specific component as an ingredient.',
    'author': 'Marwah Adel',
    'depends': ['base', 'product', 'stock','mrp','BOM_details_report', 'product_multi_uom'],
    'data': [
        'security/ir.model.access.csv',
        'views/component_final_product_view_form.xml',
        'reports/final.xml',
    ],
    'application': False,
    'installable': True,
}

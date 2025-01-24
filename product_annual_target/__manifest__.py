{
    'name': 'Product Annual Target',
    'version': '1.0',
    'summary': 'Adds Annual Target field to Products',
    'category': 'Product',
    'author': 'Marwah Adel',
    'depends': ['product', 'purchase'],
    'data': [
        'security/group.xml',
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
    ],
    'installable': True,
    'application': False,
}

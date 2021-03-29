# -*- coding: utf-8 -*-
{
    'name': "Manufacturing Api",
    'summary': """
        Module Managing Manufacturing Api's""",
    'description': """
        Module Managing Manufacturing Api's
    """,
    'author': "Muhsin, Odoo Implementors",
    'website': "http://www.odooimplementers.com/",
    'category': 'Manufacturing/Manufacturing',
    'version': '14.1',
    'depends': ['base',
                'mrp'],

    'data': [
        'security/ir.model.access.csv',
        'views/oi_api_tracker_views.xml',
        'views/product_category_view.xml',
        'views/res_users_views.xml',
    ],
}

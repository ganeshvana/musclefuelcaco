# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Purchase - Extended',
    'version': '1',
    'category': 'Purchases',
    'summary': 'Purchase - Extended',
    'description': """
            Purchase - Extended
    """,
    'depends': ['base', 'purchase'],
    'data': [
        # 'security/button_security.xml',
        'views/purchase_view.xml',
    ],
    'installable': True,
    'auto_install': False
}

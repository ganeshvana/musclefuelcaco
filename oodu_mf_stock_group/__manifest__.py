# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Restrict Stock Button',
    'version': '1',
    'category': 'Inventory',
    'summary': 'Restrict ',
    'description': """
This module shows check availability and validate button to the enabled users.
    """,
    'depends': ['base', 'stock'],
    'data': [
        'security/button_security.xml',
        'views/stock_view.xml',
    ],
    'installable': True,
    'auto_install': False
}

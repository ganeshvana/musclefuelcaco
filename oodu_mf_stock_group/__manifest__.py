# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Restrict Stock Button',
    'version': '13.0.1.0',
    'category': 'Inventory',
    'author' : 'Oodu Implementers Pvt Ltd',
    'website': 'www.odooimplementers.com'
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

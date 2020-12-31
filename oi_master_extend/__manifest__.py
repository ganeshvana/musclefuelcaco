# -*- coding: utf-8 -*-
{
    'name': "Create & Edit Access Disable",
    'summary': """Base form create and edit disable""",
    "version": "13.0.1.0",
    "category": 'Base, Purchase, Sale, Inventory, Accounting',
    'author': "Odoo Implementers Private Limited",
    "website": "http://www.odooimplementers.com",
    'license': 'AGPL-3',
    "depends": ['purchase','sale','base','sale_management','stock','account'],
    "data": [
    'security/button_security.xml',
    'views/master_views.xml'

    ],
    "application": False,
    'installable': True,
}

# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Purchase Report - Extended',
    "version": "13.0.1.0.0",
    'summary': 'Purchase Report Extended',
    'author': 'Oodu Implementers Pvt Ltd.',
    'description': """This module contains additional changes in Purchase Report""",
    'category': 'purchase',
    'depends': ['base', 'purchase'],
    'data': [
    'views/purchase_report_extend.xml',
    # 'views/stock_view.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}

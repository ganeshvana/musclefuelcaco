# -*- coding: utf-8 -*-
{
    'name': 'WhatsApp Purchase Integration',
    'version': '13.0.1.0.0',
    'author': 'Ascents Entrepreneurs',
    'license': 'OPL-1',
    'category': 'Tools',
    'summary': 'WhatsApp/Purchase Integration',
    'description': """
This module can be used to send RFQs/Purchase Orders via WhatsApp
--------------------------------------------------------------------

Send RFQs/Purchase Orders via WhatsApp
""",
    'depends': ['base', 'purchase', 'whatsapp_integration'],
    'data': [
        'views/purchase_order_form_wa_inherited.xml',
    ],
    'external_dependencies': {'python': ['phonenumbers', 'selenium']},
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'currency': 'EUR',
    'price': 30,
}

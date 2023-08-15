# -*- coding: utf-8 -*-
{
    'name': 'Partial Payment Invoice',
    'version': '1.0',
    'author': 'iWesabe',
    'description': """ Partial Payment Invoice""",
    'website': 'http://iwesabe.com/',
    'license': 'AGPL-3',
    'depends': ['base', 'bi_partial_payment_invoice'],

    'data': [
        'views/account_move_views.xml',
        'views/payment.xml',
    ],

}

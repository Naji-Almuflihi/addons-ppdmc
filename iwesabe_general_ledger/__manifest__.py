# -*- coding: utf-8 -*-
{
    'name': "Iwesabe General Ledger",

    'description': """
        Iwesabe General Ledger
    """,

    'author': "Iwesabe",
    'website': 'http://iwesabe.com/',
    'license': 'AGPL-3',
    'category': 'Account',
    'version': '14',

    'depends': ['base','account','account_reports','iwesabe_ppmdc_updates'],

    'data': [
        'views/general_ledger.xml',
        'views/partner_ledger.xml',
        'views/templates.xml',
    ],

}

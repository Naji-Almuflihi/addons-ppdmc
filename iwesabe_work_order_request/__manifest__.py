# -*- coding: utf-8 -*-
{
    'name': "Work Order Request",

    'summary': """
       Work Order Request""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Iwesabe",
    'website': "http://www.iwesabe.com",
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'iwesabe_hijri_asset',
        'maintenance',
        'helpdesk',
        'iwesabe_ppmdc_airport_management',
        'iwesabe_ppmdc_custom',
    ],

    # always loaded
    'data': [
        'security/group_property_management.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/mail_template.xml',
        'views/work_order_request_view.xml',
        'report/work_order_request_template.xml',
        'report/report_menu.xml',

    ],
    'installable': True,
    'application': False,
}

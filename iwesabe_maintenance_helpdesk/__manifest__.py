# -*- coding: utf-8 -*-
{
    'name': "iWesabe Maintenance Helpdesk",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "iWesabe",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Maintenance',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'helpdesk', 'maintenance', 'iwesabe_ppmdc_airport_management', 'report_xlsx', 'sequence_reset_period'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/helpdesk_ticket.xml',
        'views/maintenanace_request.xml',
        'views/property.xml',
        'views/templates.xml',
        'report/tanent_tenancy_report_xlsx.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

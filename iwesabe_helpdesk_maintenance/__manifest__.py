# -*- coding: utf-8 -*-
{
    'name': "Helpdesk Maintenance",

    'summary': """
        This module is integration between helpdesk and maintenance""",

    'description': """
        This module is integration between helpdesk and maintenance
    """,

    'author': "Iwesabe",
    'website': "http://www.iwesabe.com",
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['helpdesk', 'maintenance', 'repair', 'iwesabe_ppmdc_airport_management', 'hr_maintenance', 'sequence_reset_period'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/mails_maintenance.xml',
        'data/data.xml',
        'views/helpdesk_ticket_views.xml',
        'views/maintenance_request_views.xml',
        'views/maintenance_request_inerit_views.xml',
        'views/repair_order.xml',
        'views/zone_location.xml',
        'views/property.xml',
        'wizard/maintenance_request_wizard_view.xml',

    ],

}

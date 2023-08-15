# -*- coding: utf-8 -*-
{
    'name': "Airport Management",

    'summary': """
        Property Management airport:
        building, asset management""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Iwesabe",
    'website': "http://www.iwesabe.com",
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'account_asset',
        'analytic',
        'account',
        'sale',
        'base',
        'mail',
        'website_google_map',
        'iwesabe_ppmdc_custom',
        'iwesabe_hijri_asset',
        'maintenance',
        # 'iwesabe_helpdesk_maintenance'
    ],

    # always loaded
    'data': [
        'data/tenant_tenancy_data.xml',
        'data/mail_tenant_rent.xml',
        # 'data/mail_data.xml',
        'data/scheduler_email_tenant_rent.xml',
        'data/data_sequence_property.xml',
        'security/group_property_management.xml',
        'security/ir.model.access.csv',

        'report/quotation_report_templates.xml',
        'report/quotation_views.xml',
        'report/service_application_report.xml',
        'report/service_application_template.xml',
        'report/service_application_disable_template.xml',
        'report/tenancy_quotation_report_template.xml',
        'report/report_tenant_service_template.xml',

        'views/service_application_views.xml',
        'views/tenancy_service_contract_views.xml',
        'views/tenancy_service_views.xml',
        'views/tenancy_phone_extention_views.xml',
        'views/tenancy_equipment_views.xml',
        'views/tenant_tenancy_views.xml',
        'views/view_tenancy_rent_schedule.xml',
        'views/property_details_views.xml',
        'views/property_views.xml',
        'views/res_config_settings_view.xml',
        'views/maintenance_equipment_views.xml',
        'views/product_view.xml',
        'views/vlan_line.xml',
        'views/equipment_property.xml',
        'views/view_account.xml',

        # 'wizard/view_crm_make_sale.xml',
        'wizard/view_renew_tenancy_phone.xml',
        'wizard/view_renew_service.xml',

        # 'views/view_lead.xml',
        'views/view_res_partner.xml',
        'views/property_location_views.xml',
        'views/phone_extention_views.xml',

        'views/menu_property_management.xml',
        'views/property_tenancy.xml',
        'views/site.xml',
        'views/implementation_service_application.xml',
        'views/stock_location.xml',

        'wizard/view_book_available_wiz.xml',
        'wizard/view_contract_expiry_report.xml',
        'wizard/view_document_expiry_report.xml',
        'wizard/view_income_report.xml',
        'wizard/view_property_per_location.xml',
        'wizard/view_renew_tenancy.xml',
        'wizard/view_safety_certificate_report.xml',
        'wizard/view_tenancy_property_report.xml',
        'wizard/view_tenancy_tenant_report.xml',

    ],

}

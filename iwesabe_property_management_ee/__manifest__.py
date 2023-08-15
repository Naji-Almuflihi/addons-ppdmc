# See LICENSE file for full copyright and licensing details

{
    'name': 'Property Management System EE',
    'version': '14.0.1.0.0',
    'category': 'Real Estate',
    'summary': """
            Property Management System:
            building, asset management

     """,
    'author': 'iWesabe',
    'license': 'LGPL-3',
    'website': 'https://www.iwesabe.com',
    'depends': [
		'l10n_generic_coa',
		'account_asset',
		'analytic',
		'account',
		'sale_crm',
		'base',
		'mail'
		],
	'data': [
		'data/data_sequence_property.xml',
		'data/mail_tenant_rent.xml',
		'data/scheduler_email_tenant_rent.xml',
		'security/group_property_management.xml',
		'security/ir.model.access.csv',
		'security/rules_property_management.xml',
		'views/view_account_asset_asset.xml',
		'views/view_account_analytic.xml',
		'views/view_tenant_partner.xml',
		'views/view_tenancy_rent_schedule.xml',
		'views/view_property.xml',
		'views/view_account.xml',
		'views/menu_property_management.xml',
		'wizard/view_book_available_wiz.xml',
		'wizard/view_contract_expiry_report.xml',
		'wizard/view_crm_make_sale.xml',
		'wizard/view_document_expiry_report.xml',
		'wizard/view_income_report.xml',
		'wizard/view_property_per_location.xml',
		'wizard/view_renew_tenancy.xml',
		'wizard/view_safety_certificate_report.xml',
		'wizard/view_tenancy_property_report.xml',
		'wizard/view_tenancy_tenant_report.xml',
		# 'wizard/view_tenant_wizard_mail.xml',
		'views/view_lead.xml',
		'views/view_sale.xml',
		'views/view_res_partner.xml',
		'views/report_account_move.xml',
		'views/report_account_move_templates.xml',
		'views/report_contract_expiry_templates.xml',
		'views/report_document_expiry_templates.xml',
		'views/report_gfa__templates.xml',
		'views/report_income_expenditure_templates.xml',
		# 'views/report_investment_templates.xml',
		'views/report_occupancy_performance_templates.xml',
		'views/report_operational_cost_templates.xml',
		'views/report_property_external_templates.xml',
		'views/report_property_per_location_templates.xml',
		'views/report_safety_certificate_expiry_templates.xml',
		'views/report_tenancy_detail_by_property_templates.xml',
		'views/report_tenancy_detail_by_tenant_templates.xml'
    ],
    'images': ['static/description/banner.png'],
    'demo': [
		#'demo/account_asset_demo.xml'
		],
    'auto_install': False,
    'installable': True,
    'application': True,
    'currency': 'EUR',
}

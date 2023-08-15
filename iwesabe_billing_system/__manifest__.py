# -*- coding: utf-8 -*-
##############################################################################
#
#    Global Creative Concepts Tech Co Ltd.
#    Copyright (C) 2018-TODAY iWesabe (<http://www.iwesabe.com>).
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Billing System',
    'version': '1.0',
    'author': 'iWesabe',
    'summary': '',
    'description': """  """,
    'website': 'http://iwesabe.com/',
    'license': 'AGPL-3',

    'depends': ['base',
                'account',
                'report_xlsx',
                'sales_team',
                'purchase',
                'iwesabe_ppmdc_airport_management',
                'l10n_sa_invoice'
                ],

    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/ir_sequence.xml',
        'data/mail_template.xml',
        'views/ams_connection.xml',
        'views/ams_data_load.xml',
        'views/ams_data_view.xml',
        'views/ams_data_validation.xml',
        'views/generate_revenue.xml',
        'views/bill_pricing.xml',
        'views/partner.xml',
        'views/aircraft_category.xml',
        'views/product.xml',
        'views/revenue_appendix_view.xml',
        'report/invoice_appendix_report_xlsx.xml',
        'report/revenue_report_xlsx.xml',
        'report/revenue_report_vat_xlsx.xml',
        'report/invoice.xml',
        'report/invoice_appendix_pdf.xml',
        'report/flight_movement_xlsx.xml',
        'views/invoice_appendex.xml',
        'views/mail_server.xml',
        'views/airline_service_contract.xml',
        'views/bank_grantee.xml',
        'views/agent_grantee.xml',
        'views/payment.xml',
        'wizard/invoice_other_cust_wiz.xml',
        'wizard/invoice_airline_cust_wiz.xml',
        'wizard/appendix_credit_note_wiz.xml',
        'wizard/credit_note_from_appendix_wiz.xml',
    ],

    'qweb': [],

    'external_dependencies': {
        'python': ['pymssql'],
     },

    'installable': True,
    'application': True,
    'auto_install': False,
}

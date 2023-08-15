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

    'name': 'Approval Purchase Order Tripple',
    'version': '14.0.1.0',
    'category': 'Purchases',
    'license': 'AGPL-3',
    'author': 'iWesabe',
    'website': 'https://www.iwesabe.com',
    'summary': 'Approval Purchase Order Tripple: Purchase Manager -> Finance Manager -> CEO Approval',
    'description': ''' ''',
    'depends': ['purchase', 'purchase_stock', 'iwesabe_ppmdc_penalty', 'report_qweb_element_page_visibility'],
    'data': [
            'data/approve_mail_template.xml',
            'data/refuse_mail_template.xml',
            'security/ir.model.access.csv',
            'security/purchase_security.xml',
            'wizard/purchase_order_refuse_wizard_view.xml',
            'views/purchase_view.xml',
            'views/res_company_view.xml',
            'report/report_templates.xml',
            'report/purchase_order_form_52k.xml',
             ],
    'installable': True,
    'auto_install': False
}


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
    'name': 'PPMDC Custom',
    'version': '1.0',
    'author': 'iWesabe',
    'summary': '',
    'description': """  """,
    'website': 'http://iwesabe.com/',
    'license': 'AGPL-3',
    'depends': ['hr', 'maintenance', 'account_asset', 'repair', 'account', 'purchase', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'security/security_views.xml',
        'data/ir_sequence.xml',
        'data/mail_template.xml',
        'wizard/view_renew_tenancy_equipment.xml',

        'views/hr_employee_views.xml',
        'views/product_views.xml',
        'views/maintenance_equipment_views.xml',
        'views/account_asset_views.xml',
        'views/repair_views.xml',
        'views/maintenance_request_views.xml',
        # 'views/tenancy_equipment_views.xml',
        # 'views/tenant_tenancy_views.xml',
        'views/maintenance_menu_views.xml',
        'views/maintenance_plans_views.xml',
        'views/partner_view.xml',
        'views/customer_type_view.xml',
        'views/system_category_view.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}

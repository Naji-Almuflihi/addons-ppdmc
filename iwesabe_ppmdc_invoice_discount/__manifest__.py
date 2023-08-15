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
    'name': 'Invoice and Vendor Bills Discount',
    'version': '1.0',
    'category': 'Invoicing',
    'summary': 'Discount on Invoices and Vendor Bills',
    'description': """
                This odoo app helps user to apply discount on customer invoice and vendor bills.
                """,
    'author': 'iWesabe',
    'website': 'http://iwesabe.com/',
    'depends': ['sale_management', 'purchase', 'account'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/discount_type_view.xml',
        'views/account_move_view.xml',
        'reports/account_report.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

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
    'name': 'PPMDC Updates',
    'version': '1.0',
    'author': 'iWesabe',
    'summary': '',
    'description': """  """,
    'website': 'http://iwesabe.com/',
    'license': 'AGPL-3',
    'depends': ['hr_expense', 'stock', 'purchase', 'account_accountant', 'account', 'contract', 'iwesabe_ppmdc_airport_management', 'mail', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'security/security_views.xml',
        'data/mail.xml',
        'views/views.xml',
        'views/site.xml',
        'views/partner.xml',
        'views/hr_expense_sheet.xml',
        # 'views/assets.xml',

    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}

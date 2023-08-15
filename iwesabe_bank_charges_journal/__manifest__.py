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
    'name': 'Bank Charges Journal',
    'version': '14.0',
    'category': 'Accounting',
    'author': 'iWesabe',
    'summary': '',
    'description': """  """,
    'website': 'https://www.iwesabe.com/',
    'license': 'AGPL-3',
    'depends': ['web', 'base','account','account_accountant'],
    'data': [
        'views/account_view.xml',
        'views/account_payment.xml',
    ],
    'demo': [],
    'test': [],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
}

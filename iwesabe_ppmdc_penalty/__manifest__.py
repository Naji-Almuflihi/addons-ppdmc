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
    'name': 'PPMDC Penalty',
    'version': '1.0',
    'author': 'iWesabe',
    'summary': '',
    'description': """  """,
    'website': 'http://iwesabe.com/',
    'license': 'AGPL-3',
    'depends': ['base', 'mail', 'account', 'contract', 'purchase'],
    'data': [
        'security/account_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/billing_manager_template.xml',
        # 'views/cleaning_penalty_views.xml',
        # 'views/maintenance_penalty_views.xml',
        # 'views/common_penalty_views.xml',
        'views/penalty_template_views.xml',
        'views/penalty_item_views.xml',
        'views/account_move_views.xml',
        'views/contract_views.xml',
        'views/penalty_sheet_view.xml',
        'views/invoice_document.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}

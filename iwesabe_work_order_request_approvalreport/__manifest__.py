# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
##############################################################################
#
#    Global Creative Concepts Tech Co Ltd.
#    Copyright (C) 2018-TODAY iWesabe (<https://www.iwesabe.com>).
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL-3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL-3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL-3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "Work Order Request Approval",

    'summary': """
       Work Order Request Multilevel Approval and report""",
    'author': "Iwesabe",
    'website': "http://www.iwesabe.com",
    'license': 'LGPL-3',
    'version': '15.0.0.0',


    # any module necessary for this one to work correctly
    'depends': [
        'iwesabe_work_order_request'
    ],

    # always loaded
    'data': [
        'reports/custom_layout.xml',
        'reports/work_order_pdf_reports.xml',
    ],

}

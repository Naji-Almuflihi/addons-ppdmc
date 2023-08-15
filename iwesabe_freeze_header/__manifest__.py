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
    'name': "Freeze List View Header",

    'summary': """
        To freeze list view's & grid view's header, very helpful when dealing with many record.
    """,

    'description': """
        To freeze list view's & grid view's header, very helpful when dealing with many record.
    """,
    'author': 'iWesabe',
    'website': 'http://iwesabe.com/',
    'license': 'AGPL-3',
    'category': 'web',
    'version': '14.0.0.1',
    'images': ['images/main_screenshot.png'],
    'depends': ['web', 'base'],
    'data': [
        "views/freeze_head.xml",
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

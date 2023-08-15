# * coding: utf8 *
##############################################################################
#
#    Global Creative Concepts Tech Co Ltd.
#    Copyright (C) 2018TODAY iWesabe (<http://www.iwesabe.com>).
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
    'name': 'iwesabe Bank Guarantee',
    'version': '14.0.0',
    'category': '',
    'description': """Qomel
    """,
    'author': 'iWesabe',
    'website': 'https://www.iwesabe.com',
    'description':
        """
        """,
    'depends': ['base','account'],
    'data': [
        'security/ir.model.access.csv',
        'data/renew_cron.xml',
        'views/data.xml',
        'views/email_template.xml',
        'views/res_config_settings.xml',
        'views/bank_guarantee.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'installable': True,
    'application': True
}

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
    'name': 'Purchase Approval',
    'version': '14.0.0.0',
    'category': 'Purchases',
    'sequence': 15,
    'summary': 'This app helps you to approval process for Purchase Order while confirm Purchase order.',
    'description': """
        This app helps you to approval process for Purchase Order while confirm Purchase order.
    """,
    'website': 'https://www.iwesabe.com',
    'price': 49,
    'currency': "EUR",
    'author': 'iWesabe',
    'depends': ['base', 'purchase','sale'],
    'data': [
        'security/purchase_groups.xml',
        'views/purchase_config_setting_view.xml',
        'views/sales.xml',
        'views/purchase_order_view.xml'],
    'demo': [],
    'css': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    # "images":['static/description/Banner.png'],
}

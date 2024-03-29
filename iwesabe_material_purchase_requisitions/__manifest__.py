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
    'name': 'Product/Material Purchase Requisitions by Employees/Users',
    'version': '2.7.3',
    'price': 79.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This module allow your employees/users to create Purchase Requisitions.""",
    'description': """
    Material Purchase Requisitions
    This module allowed Purchase requisition of employee.
Purchase_Requisition_Via_iProcurement
Purchase Requisitions
Purchase Requisition
iProcurement
Inter-Organization Shipping Network
Online Requisitions
Issue Enforcement
Inventory Replenishment Requisitions
Replenishment Requisitions
MRP Generated Requisitions
generated Requisitions
purchase Sales Orders
Complete Requisitions Status Visibility
Using purchase Requisitions
purchase requisitions
replenishment requisitions
employee Requisition
employee purchase Requisition
user Requisition
stock Requisition
inventory Requisition
warehouse Requisition
factory Requisition
department Requisition
manager Requisition
Submit requisition
Create purchase Orders
purchase Orders
product Requisition
item Requisition
material Requisition
product Requisitions
material purchase Requisition
material Requisition purchase
purchase material Requisition
product purchase Requisition
item Requisitions
material Requisitions
products Requisitions
purchase Requisition Process
Approving or Denying the purchase Requisition
Denying purchase Requisition​
construction management
real estate management
construction app
Requisition
Requisitions
indent management
indent
indent stock
indent system
indent request
indent order
odoo indent
internal Requisitions
* INHERIT hr.department.form.view (form)
* INHERIT hr.employee.form.view (form)
* INHERIT stock.picking.form.view (form)
purchase.requisition search (search)
purchase.requisition.form.view (form)
purchase.requisition.view.tree (tree)
purchase_requisition (qweb)
Main Features:
allow your employees to Create Purchase Requisition.
Employees can request multiple material/items on single purchase Requisition request.
Approval of Department Head.
Approval of Purchase Requisition Head.
Email notifications to Department Manager, Requisition Manager for approval.
- Request for Purchase Requisition will go to stock/warehouse as internal picking / internal order and purchase order.
- Warehouse can dispatch material to employee location and if material not present then procurment will created by Odoo standard.
- Purchase Requisition user can decide whether product requested by employee will come from stock/warehouse directly or it needs to be purchase from vendor. So we have field on requisition lines where responsible can select Requisition action: 1. Purchase Order 2. Internal Picking. If option 1 is selected then system will create internal order / internal picking request and if option 2 is selected system will create multiple purchase order / RFQ to vendors selected on lines.
- For more details please see Video on live preview or ask us by email...


    """,
    'author': 'iWesabe',
    'website': 'http://iwesabe.com/',
    'images': ['static/description/img1.jpeg'],
    'category': 'Warehouse',
    'depends': [
        'stock',
        'hr',
        'purchase',
        'purchase_requisition',
        'iwesabe_purchase_requisition',
    ],
    'data': [
        'security/security.xml',
        'security/multi_company_security.xml',
        'security/ir.model.access.csv',
        'data/purchase_requisition_sequence.xml',
        'data/employee_purchase_approval_template.xml',
        'data/confirm_template_material_purchase.xml',
        'data/notification_mail_template.xml',
        'report/purchase_requisition_report.xml',
        'views/purchase_requisition_view.xml',
        'views/hr_employee_view.xml',
        'views/hr_department_view.xml',
        'views/stock_picking_view.xml',
        # 'views/purchase_order_view.xml',
    ],
    'installable': True,
    'application': False,
}

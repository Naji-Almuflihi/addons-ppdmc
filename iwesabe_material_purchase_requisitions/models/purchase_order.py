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

from odoo import models, fields, api,_
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    custom_requisition_id = fields.Many2one(
        'material.purchase.requisition',
        string='Requisitions',
        copy=False
    )
    requisition_id = fields.Many2one(
        'purchase.requisition',
        string='Purchase Agreement',
        copy=False,
        readonly=True
    )
    origin = fields.Char(
        'Source Document',
        copy=False,
        readonly=True
    )
    date_order = fields.Datetime(
        'Order Deadline', required=True,
        states=READONLY_STATES, index=True,
        copy=False, default=fields.Datetime.now,
        readonly=True,
        help="Depicts the date within which the Quotation should be confirmed and converted into a purchase order.")

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    custom_requisition_line_id = fields.Many2one(
        'material.purchase.requisition.line',
        string='Requisitions Line',
        copy=False
    )

    discount = fields.Float('Discount %')

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result

        # Reset date, price and quantity since _onchange_quantity will provide default values
        self.date_planned = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.price_unit = self.product_qty = 0.0
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}

        product_lang = self.product_id.with_context(
            lang=self.partner_id.lang,
            partner_id=self.partner_id.id,
        )
        self.name = product_lang.display_name
        if product_lang.description_purchase:
            self.name =  product_lang.description_purchase

        self._compute_tax_id()

        self._suggest_quantity()
        self._onchange_quantity()

        return result

    @api.depends('product_qty', 'price_unit', 'taxes_id','discount')
    def _compute_amount(self):
        for line in self:
            taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.product_qty, product=line.product_id, partner=line.order_id.partner_id)
            if line.discount:
                discount = (line.price_unit * line.discount * line.product_qty)/100
                line.update({
                    'price_tax': taxes['total_included'] - taxes['total_excluded'],
                    'price_total': taxes['total_included'] ,
                    'price_subtotal': taxes['total_excluded'] - discount,
                })
            else:
                line.update({
                    'price_tax': taxes['total_included'] - taxes['total_excluded'],
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    custom_requisition_id = fields.Many2one('material.purchase.requisition', string='Requisitions', copy=False)

    def write(self, vals):
        old_state = self.state
        template_id = self.env.ref('iwesabe_material_purchase_requisitions.email_purchase_aggrement_state_notification')
        res = super(PurchaseRequisition, self).write(vals)
        if 'state' in vals and self.custom_requisition_id:
            new_state = vals['state']
            if old_state != new_state and self.custom_requisition_id:
                email_to = self.custom_requisition_id.employee_id and self.custom_requisition_id.employee_id.work_email or self.custom_requisition_id.employee_id.user_id.email
                if email_to:
                    template_id.write({'email_to': email_to})
                    template_id.send_mail(self.id, force_send=True)
        return res

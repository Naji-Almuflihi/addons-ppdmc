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

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to_finance_manager_approve', 'To Finance Manager Approval'),
        ('to_purchase_manager_approve', 'To Purchase Manager Approval'),
        ('to_general_manager_approve', 'To General Manager Approval'),
        ('to_ceo_approve', 'To CEO Approval'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')

    def button_confirm(self):
        res = self.env['res.config.settings'].sudo().search([], order="id desc", limit=1)
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            # if order.company_id.po_double_validation == 'one_step' or (
            #         order.company_id.po_double_validation == 'two_step' and order.amount_total < self.env.user.company_id.currency_id.compute(
            #         order.company_id.po_double_validation_amount, order.currency_id)) \
            #         or order.user_has_groups('purchase.group_purchase_manager'):
            #     order.button_approve()
            # else:
            #     order.write({'state': 'to_finance_manager_approve'})
            # if res.po_order_approval == True and order.amount_total <= res.po_double_validation_amount:
            order.write({'state': 'budget_approval'})
        return True

    def button_finance_manager_approve(self):
        for order in self:
            order.write({'state': 'to_purchase_manager_approve', 'date_approve': fields.Date.context_today(self)})

    def button_purchase_manager_approve(self):
        for order in self:
            order.write({'state': 'to_general_manager_approve', 'date_approve': fields.Date.context_today(self)})

    def button_general_manager_approve(self, force=False):
        res = self.env['res.config.settings'].sudo().search([], order="id desc", limit=1)
        if res.second_approval == True and self.amount_total >= res.second_approval_minimum_amount:
            self.write({'state': 'to_ceo_approve'})
        else:
            self.write({'state': 'purchase', 'date_approve': fields.Date.context_today(self)})
            self._create_picking()
            self.filtered(
                lambda p: p.company_id.po_lock == 'lock').write({'state': 'done'})
        return {}

    def button_ceo_approve(self):
        for order in self:
            order.write({'state': 'purchase', 'date_approve': fields.Date.context_today(self)})
            order._create_picking()
            order.filtered(
                lambda p: p.company_id.po_lock == 'lock').write({'state': 'done'})

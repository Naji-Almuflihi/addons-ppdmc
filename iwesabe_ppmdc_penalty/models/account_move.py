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
from odoo import models, api, fields, _

from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends('contract_id')
    def _get_contract(self):
        for rec in self:
            if rec.contract_id:
                if rec.state == 'ceo_approved':
                    rec.contract = True
                else:
                    rec.contract = False
            else:
                if rec.state == 'posted':
                    rec.contract = False
                else:
                    rec.contract = True

    # amount_total = fields.Monetary(string="Total", compute="set_total_amount", store=True)
    contract_id = fields.Many2one('contract.contract')
    total_penalty = fields.Float(compute='compute_penalty_total')
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('discount_computation', 'Discount Computation'),
                   ('waiting_approval', 'Waiting For Support Approval'),
                   ('support_approved', 'Support Approved'),
                   ('waiting_for_ceo_approval', 'Waiting For CEO Approval'),
                   ('ceo_approved', 'CEO Approved'), ('posted', 'Posted'), ('cancel', 'cancelled')],
        string="Status", default="draft")
    contract = fields.Boolean('Contract', compute='_get_contract')
    penalty = fields.Boolean('Penalty', default=False)
    penalty_sheet_id = fields.Many2one('penalty.sheet',  string="Penalty Sheet")  # related="contract_id.penalty_sheet_id",

    # @api.depends('contract_id')
    # def _comoute_contract_id(self):
    #     for rec in self:
    #         count_panalty = self.env['penalty.sheet'].search(
    #             [('contract_id', '=', rec.contract_id.id), ('move_id', '=', rec.id),
    #              ('id', '=', rec.penalty_sheet_id.id)])
    #         print(">>>count_panalty>>>>>>>>>", count_panalty)
    #         for penalty in count_panalty:
    #             rec.total_penalty = penalty.penalty_total

    def ask_to_support_approvals(self):
        for rec in self:
            if not rec.penalty:
                rec.action_post()
            else:
                rec.action_post_custom()
            rec.state = 'waiting_approval'
            employee_mail_template = self.env.ref('iwesabe_ppmdc_penalty.email_account_support_approval')
            employee_mail_template.sudo().send_mail(self.id)
            if rec.company_id.general_manager_id:
                thread_pool = self.sudo().env['mail.thread']
                thread_pool.message_notify(
                    partner_ids=[rec.company_id.general_manager_id.partner_id.id],
                    subject=str('Billing Support Notification'),
                    body=str('This Bill ' + str(
                        rec.name) + ' Need Your Approval ') + ' click here to open: <a target=_BLANK href="/web?#id=' + str(
                        rec.id) + '&view_type=form&model=account.move&action=" style="font-weight: bold">' + str(
                        rec.name) + '</a>',
                    email_from=self.env.user.company_id.catchall_formatted or self.env.user.company_id.email_formatted, )

    def approve_billing_manager(self):
        for rec in self:
            billing_user_id = self.env['res.users'].has_group('account.group_account_invoice')
            if billing_user_id or rec.user_id == self.env.uid:
                rec.state = 'support_approved'
                employee_mail_template = self.env.ref('iwesabe_ppmdc_penalty.email_account_billing_approval')
                employee_mail_template.sudo().send_mail(self.id)

    def waiting_for_ceo_approval(self):
        employee_mail_template = self.env.ref('iwesabe_ppmdc_penalty.email_account_send_to_ceo_approval')
        employee_mail_template.sudo().send_mail(self.id)
        if self.company_id.director_manager_id:
            thread_pool = self.sudo().env['mail.thread']
            thread_pool.message_notify(
                partner_ids=[self.company_id.director_manager_id.partner_id.id],
                subject=str('Billing CEO Notification'),
                body=str('This Bill ' + str(
                    self.name) + ' Need Your Approval ') + ' click here to open: <a target=_BLANK href="/web?#id=' + str(
                    self.id) + '&view_type=form&model=account.move&action=" style="font-weight: bold">' + str(
                    self.name) + '</a>',
                email_from=self.env.user.company_id.catchall_formatted or self.env.user.company_id.email_formatted, )

        self.state = 'waiting_for_ceo_approval'

    def ceo_approved(self):
        for rec in self:
            rec.state = 'ceo_approved'

    def compute_penalty_disc(self):
        users_ids = self.contract_id.contract_penalty_line_ids.mapped("responsible_id")
        pen_sheet = self.env['penalty.sheet'].search(
            [('move_id', '=', self.id), ('contract_id', '=', self.contract_id.id)])
        for rec in self:
            if pen_sheet:
                rec.penalty = True
                for pen in pen_sheet:
                    if pen.state != 'confirmed':
                        raise ValidationError(_("Not all penalty sheets are confirmed!"))
                    rec.apply_discount = True
                    rec.onchange_apply_discount()
                    # rec._onchange_discount_account()
                    rec.discount_type_id = rec.env['discount.type'].search([('name', '=', 'Fixed')]).id
                    rec.discount_value = rec.total_penalty
                    # rec.onchange_type()
                    rec.state = 'discount_computation'

    def action_post_custom(self):
        res = super(AccountMove, self).action_post()
        for rec in self:
            if rec.amount_after_discount >= 1:
                prev_credit = self.env['account.move.line'].search(
                    [('credit', '>', 0.0), ('move_id', '=', rec.id), ('exclude_from_invoice_tab', '=', True)])
                for credit_rec in prev_credit:
                    credit_val = credit_rec.credit - rec.amount_after_discount
                    if credit_rec:
                        credit_rec.with_context(check_move_validity=False).write({
                            # 'account_id': rec.line_ids.account_id[0].id,
                            'account_id': rec.partner_id.property_account_payable_id.id,
                            'credit': credit_val,
                            'debit': 0.0,
                            'amount_currency': rec.amount_after_discount,
                            'price_unit': rec.amount_after_discount,
                            'price_total': rec.amount_after_discount,
                            'move_id': rec.id,
                            'exclude_from_invoice_tab': True,
                        })
                    account = False
                    if rec.move_type == 'out_invoice':
                        account = rec.out_discount_account
                    if rec.move_type == 'in_invoice':
                        account = rec.in_discount_account
                    self.env['account.move.line'].with_context(check_move_validity=False).create({
                        'account_id': account.id,
                        'name': "Discount",
                        'credit': rec.amount_after_discount,
                        'debit': 0.0,
                        'amount_currency': rec.amount_after_discount,
                        'price_unit': rec.amount_after_discount,
                        'price_total': rec.amount_after_discount,
                        'move_id': rec.id,
                        'exclude_from_invoice_tab': True,
                    })
        return res

    def action_get_penalty_sheet(self):
        action = self.env.ref('iwesabe_ppmdc_penalty.penalty_sheet_action').read([])[0]
        for rec in self:
            sheet_ids = self.env['penalty.sheet'].search(
                [('contract_id', '=', rec.contract_id.id), ('move_id', '=', rec.id)])
            action['domain'] = [('id', 'in', sheet_ids.ids)]
            return action

    @api.depends('contract_id')
    def compute_penalty_total(self):
        for rec in self:
            penalty_total = 0.0
            sheet_ids = self.env['penalty.sheet'].search(
                [('contract_id', '=', rec.contract_id.id), ('move_id', '=', rec.id), ('state', '=', 'confirmed')])
            for sheet in sheet_ids:
                penalty_total += sheet.penalty_total
            self.total_penalty = penalty_total

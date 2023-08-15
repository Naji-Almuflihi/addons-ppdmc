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

from odoo import api, fields, models


# class AccountRegisterPayment(models.Model):
#     _name = 'amount.register.payment'

#     payment_id = fields.Many2one(comodel_name="account.move", string="", required=False, )
#     amount = fields.Float(string="Amount",  required=False, )
#     date = fields.Date(string="Date", required=False, )


# class AccountPaymentRegisterInherit(models.TransientModel):
#     _inherit = 'account.payment.register'

#     @api.depends('source_amount', 'source_amount_currency', 'source_currency_id', 'company_id', 'currency_id',
#                  'payment_date')
#     def _compute_amount(self):

#         account_move_record = self.env['account.move'].browse(self._context.get('active_ids', []))
#         for move in account_move_record:
#             self.amount = move.amount_residual
#             self.payment_difference = 0
#             self.payment_difference = move.amount_residual-self.amount

#         res = super(AccountPaymentRegisterInherit, self)._compute_amount()
#         return res

#     @api.depends('amount')
#     def _compute_payment_difference(self):
#         res = super(AccountPaymentRegisterInherit, self)._compute_payment_difference()
#         account_move_record = self.env['account.move'].browse(self._context.get('active_ids', []))
#         for move in account_move_record:
#             self.payment_difference = 0
#             self.payment_difference = move.amount_residual-self.amount
#         return res

#     def action_create_payments(self):
#         res = super(AccountPaymentRegisterInherit, self).action_create_payments()
#         lines_list = []
#         account_move_record = self.env['account.move'].browse(self._context.get('active_ids', []))
#         for move in account_move_record:
#             move.amount_residual = self.amount
#             move.check_register = True
#             lines_list.append((0, 0, {'amount': self.amount, 'date': self.payment_date}))
#             move.update({'register_payments_ids': lines_list})
#         return res


class account_account(models.Model):
    _inherit = 'account.account'

    discount_account = fields.Boolean('Discount Account')


class account_move(models.Model):
    _inherit = 'account.move'

    # register_payments_ids = fields.One2many(comodel_name="amount.register.payment", inverse_name="payment_id", string="", required=False, )

    check_register = fields.Boolean(string="")

    # def _get_reconciled_info_JSON_values(self):
    #     res = super(account_move, self)._get_reconciled_info_JSON_values()
    #     for lin in self.register_payments_ids:
    #         if res[-1]['date'] == lin.date:
    #             res[-1]['amount'] = lin.amount
    #     return res

    def _compute_amount_after_discount(self):
        res = discount = 0.0
        discount_type_percent = self.env['ir.model.data'].xmlid_to_res_id(
            'iwesabe_ppmdc_invoice_discount.discount_type_percent_id')
        discount_type_fixed = self.env['ir.model.data'].xmlid_to_res_id(
            'iwesabe_ppmdc_invoice_discount.discount_type_fixed_id')

        for self_obj in self:
            if not self_obj.apply_discount:
                self_obj.discount_value = 0.0
                self_obj.discount_type_id = False
                self_obj.out_discount_account = False
                self_obj.in_discount_account = False
                move_line = self.line_ids.filtered(lambda x: x.discount_line)
                move_id = move_line.move_id
                currency_id = move_id.currency_id
                company_currency = move_id.company_currency_id
                if move_id.move_type == 'entry' or move_id.is_outbound():
                    sign = 1
                else:
                    sign = -1
                if move_line:
                    if move_id.is_inbound():
                        move_line_id = self.line_ids.filtered(
                            lambda x: not x.discount_line and (x.debit > 0.0 and x.credit == 0.0))
                        credit_lines = self.line_ids.filtered(lambda line: line.credit > 0.0)
                        total_debit = sum(line.amount_currency for line in credit_lines)
                        if currency_id != company_currency:
                            move_line_id.update({
                                'amount_currency': (sign * total_debit)
                            })
                            move_line.update({
                                'amount_currency': 0.00,
                                'debit': 0.00
                            })
                            move_line_id._onchange_amount_currency()
                        else:
                            move_line_id.update({
                                'debit': (sign * total_debit)
                            })
                            move_line.update({
                                'debit': 0.00
                            })
                            # discount_value = move_line.amount_currency
                    else:
                        move_line_id = self.line_ids.filtered(
                            lambda x: not x.discount_line and (x.debit == 0.0 and x.credit > 0.0))
                        debit_lines = self.line_ids.filtered(lambda line: line.debit > 0.0)
                        total_credit = sum(line.amount_currency for line in debit_lines)
                        if currency_id != company_currency:
                            move_line_id.update({'amount_currency': (sign * total_credit)})
                            move_line.update({
                                'amount_currency': 0.00,
                                'credit': 0.00
                            })
                        else:
                            move_line_id.update({'credit': (sign * total_credit)})
                            move_line.update({'credit': 0.00})
                    return 0.00
            if self_obj.discount_type_id.id == discount_type_fixed:
                res = self_obj.discount_value
            elif self_obj.discount_type_id.id == discount_type_percent:
                res = self_obj.amount_untaxed * (self_obj.discount_value / 100)
            else:
                res = discount
            return res

    @api.onchange('apply_discount')
    def onchange_apply_discount(self):
        if self.apply_discount:
            if self.move_type == 'out_invoice':
                account_search = self.env['account.account'].search(
                    [('user_type_id.internal_group', '=', 'expense'), ('discount_account', '=', True)], limit=1)
                if account_search:
                    self.out_discount_account = account_search and account_search.id
            if self.move_type == 'in_invoice':
                account_search = self.env['account.account'].search(
                    [('user_type_id.internal_group', '=', 'income'), ('discount_account', '=', True)], limit=1)
                if account_search:
                    self.in_discount_account = account_search and account_search.id

    @api.onchange('out_discount_account', 'in_discount_account', 'discount_type_id')
    def _onchange_discount_account(self):
        if self.move_type == 'out_invoice' and not self.out_discount_account:
            return
        if self.move_type == 'in_invoice' and not self.in_discount_account:
            return
        move_line = self.line_ids.filtered(lambda x: x.discount_line)

        if self.is_inbound():
            discount_account = self.out_discount_account and self.out_discount_account.id
        else:
            discount_account = self.in_discount_account and self.in_discount_account.id

        if move_line:
            move_line.update({
                'account_id': discount_account,
                'name': self.discount_type_id and self.discount_type_id.name or '',
            })
        else:
            discount_line = {
                'account_id': discount_account,
                'price_unit': 0.00,
                'quantity': 1,
                'name': self.discount_type_id and self.discount_type_id.name or '',
                'exclude_from_invoice_tab': True,
                'discount_line': True,
            }

            self.with_context(check_move_validity=False).update({'line_ids': [(0, 0, discount_line)]})

    discount_type_id = fields.Many2one('discount.type', 'Discount Type')
    discount_value = fields.Float('Discount Value', )
    out_discount_account = fields.Many2one('account.account', 'Discount Account')
    in_discount_account = fields.Many2one('account.account', 'Discount Account')
    amount_after_discount = fields.Monetary('Discount Amount', readonly=True, tracking=True)
    amount_after_discount2 = fields.Monetary(string="")

    apply_discount = fields.Boolean('Apply Discount')
    discount_move_line_id = fields.Many2one('account.move.line', 'Discount Line')
    purchase_order = fields.Boolean('is a PO', default=False)

    # @api.depends(
    #     'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
    #     'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
    #     'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
    #     'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
    #     'line_ids.debit',
    #     'line_ids.credit',
    #     'line_ids.currency_id',
    #     'line_ids.amount_currency',
    #     'line_ids.amount_residual',
    #     'line_ids.amount_residual_currency',
    #     'line_ids.payment_id.state',
    #     'line_ids.full_reconcile_id',
    #     'discount_type_id',
    #     'apply_discount')
    def _compute_amount(self):
        pass
        # for move in self:
        #     # total = 0
        #     # amount_after_discount = 0
        #     # amount_after_discount2 = 0
        #     # amount_total = 0
        #     # # for amount in move.register_payments_ids:
        #     # #     total += amount.amount
        #     # discount = move._compute_amount_after_discount()
        #     # amount_after_discount = move._compute_amount_after_discount()
        #     # amount_after_discount2 = move._compute_amount_after_discount()
        #     # amount_total = move.amount_total - discount
        #     # move.amount_total = amount_total
        #     # if not move.check_register:
        #     #     move.amount_residual = move.amount_total
        #     # if move.check_register:

        #     #     move.amount_residual = move.amount_total - total
        #     #     if move.amount_residual == 0:
        #     #         move.payment_state = 'paid'
        #     # move.amount_after_discount2 = amount_after_discount2
        #     # move.amount_after_discount = amount_after_discount
        # res = super(account_move, self)._compute_amount()
        # return res

    @api.onchange('discount_type_id', 'discount_value', 'invoice_line_ids', 'line_ids')
    def onchange_type(self):
        move_line = self.line_ids.filtered(lambda x: x.discount_line)

        if move_line and move_line.move_id.is_invoice():
            move_id = move_line.move_id
            currency_id = move_id.currency_id
            company_currency = move_id.company_currency_id
            if move_id.move_type == 'entry' or move_id.is_outbound():
                sign = 1
            else:
                sign = -1

            discount_value = move_id._compute_amount_after_discount()
            if move_id.is_inbound():
                move_line_id = self.line_ids.filtered(
                    lambda x: not x.discount_line and (x.debit > 0.0 and x.credit == 0.0))
                credit_lines = self.line_ids.filtered(lambda line: line.credit > 0.0)
                total_debit = sum(line.amount_currency for line in credit_lines)
                if currency_id != company_currency:
                    move_line_id.update({
                        'amount_currency': (sign * total_debit) - discount_value
                    })

                    move_line_id._onchange_amount_currency()
                    to_ = currency_id._convert(discount_value, company_currency, move_id.company_id, move_id.date)

                    move_line.update({
                        'amount_currency': discount_value,
                        'debit': to_,
                    })
                else:
                    move_line_id.update({
                        'debit': (sign * total_debit) - discount_value
                    })
                    move_line.update({
                        'debit': discount_value
                    })
            else:
                move_line_id = self.line_ids.filtered(
                    lambda x: not x.discount_line and (x.debit == 0.0 and x.credit > 0.0))
                debit_lines = self.line_ids.filtered(lambda line: line.debit > 0.0)
                total_credit = sum(line.amount_currency for line in debit_lines)
                if currency_id != company_currency:
                    move_line_id.update({'amount_currency': (sign * total_credit) - discount_value})

                    move_line_id._onchange_amount_currency()
                    to_ = currency_id._convert(discount_value, company_currency, move_id.company_id, move_id.date)

                    move_line.update({
                        'amount_currency': discount_value,
                        'credit': to_,
                    })
                else:
                    move_line_id.update({'credit': (sign * total_credit) - discount_value})
                    move_line.update({'credit': discount_value})


class account_move_line(models.Model):
    _inherit = 'account.move.line'

    discount_line = fields.Boolean('is a discount line')

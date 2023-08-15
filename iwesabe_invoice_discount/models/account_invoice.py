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
from odoo.exceptions import ValidationError


class GlobalDiscountInvoice(models.Model):
    _inherit = "account.move"

    global_discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Discount Type', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, default='percent')
    global_discount_rate = fields.Float('Discount', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    amount_discount = fields.Monetary(string='Discount', compute='_compute_amount', store=True, track_visibility='always')

    sales_discount_account_id = fields.Many2one('account.account', 'Discount Account')
    purchase_discount_account_id = fields.Many2one('account.account', 'Discount Account')

    @api.depends(
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'global_discount_type',
        'global_discount_rate')
    def _compute_amount(self):
        super(GlobalDiscountInvoice, self)._compute_amount()
        for rec in self:
            if not ('global_tax_rate' in rec):
                rec.calculate_discount()
            sign = rec.move_type in ['in_refund', 'out_refund'] and -1 or 1
            # rec.amount_total_company_signed = rec.amount_total * sign
            rec.amount_total_signed = rec.amount_total * sign

    def calculate_discount(self):
        for rec in self:
            if rec.global_discount_type == "amount":
                rec.amount_discount = rec.global_discount_rate if rec.amount_untaxed > 0 else 0
            elif rec.global_discount_type == "percent":
                if rec.global_discount_rate != 0.0:
                    rec.amount_discount = (rec.amount_untaxed + rec.amount_tax) * rec.global_discount_rate / 100
                else:
                    rec.amount_discount = 0
            elif not rec.global_discount_type:
                rec.global_discount_rate = 0
                rec.amount_discount = 0
            rec.amount_total = rec.amount_tax + rec.amount_untaxed - rec.amount_discount
            rec.update_invoice_bill_discount()

    @api.constrains('global_discount_rate')
    def check_discount_value(self):
        if self.global_discount_type == "percent":
            if self.global_discount_rate > 100 or self.global_discount_rate < 0:
                raise ValidationError('You cannot enter percentage value greater than 100.')
        else:
            if self.global_discount_rate < 0 or self.amount_untaxed < 0:
                raise ValidationError(
                    'You cannot enter discount amount greater than actual cost or value lower than 0.')

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        res = super(GlobalDiscountInvoice, self)._prepare_refund(invoice, date_invoice=None, date=None, description=None, journal_id=None)
        res['global_discount_rate'] = self.global_discount_rate
        res['global_discount_type'] = self.global_discount_type
        return res

    def update_invoice_bill_discount(self):
        """This Function Updates the Universal Discount through Sale Order"""
        for rec in self:
            already_exists = self.line_ids.filtered(lambda line: line.name and line.name.find('Universal Discount') == 0)
            terms_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
            other_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
            if already_exists:
                amount = rec.amount_discount
                if rec.sales_discount_account_id and (rec.move_type == "out_invoice" or rec.move_type == "out_refund") and amount > 0:
                    if rec.move_type == "out_invoice":
                        already_exists.update({'debit': amount > 0.0 and amount or 0.0, 'credit': amount < 0.0 and -amount or 0.0})
                    else:
                        already_exists.update({'debit': amount < 0.0 and -amount or 0.0, 'credit': amount > 0.0 and amount or 0.0})
                if rec.purchase_discount_account_id and (rec.move_type == "in_invoice" or rec.move_type == "in_refund") and amount > 0:
                    if rec.move_type == "in_invoice":
                        already_exists.update({'debit': amount < 0.0 and -amount or 0.0, 'credit': amount > 0.0 and amount or 0.0})
                    else:
                        already_exists.update({'debit': amount > 0.0 and amount or 0.0, 'credit': amount < 0.0 and -amount or 0.0})
                total_balance = sum(other_lines.mapped('balance'))
                total_amount_currency = sum(other_lines.mapped('amount_currency'))
                if not sum(terms_lines.mapped('debit')) == rec.amount_total_signed:
                    discount_percent = 0.0
                    total_discount = 0.0
                    for record in range(0, len(terms_lines)):
                        if len(self.invoice_payment_term_id.line_ids) >= len(terms_lines):
                            if self.invoice_payment_term_id.line_ids[record].value_amount:
                                total_discount += self.invoice_payment_term_id.line_ids[record].value_amount
                            else:
                                discount_percent = 100 - total_discount
                            terms_lines[record].update({
                                'amount_currency': -total_amount_currency,
                                'debit': (self.amount_total * (self.invoice_payment_term_id.line_ids[record].value_amount if not discount_percent else discount_percent) / 100) if total_balance < 0.0 else 0.0,
                                'credit': ((self.amount_total * self.invoice_payment_term_id.line_ids[record].value_amount) / 100) if total_balance > 0.0 else 0.0
                            })
                        else:
                            terms_lines[record].update({
                                'amount_currency': -total_amount_currency,
                                'debit': self.amount_total if total_balance < 0.0 else 0.0,
                                'credit': self.amount_total if total_balance > 0.0 else 0.0
                            })
                else:
                    for record in terms_lines:
                        if rec.global_discount_type == "percent":
                            record.update({
                                'amount_currency': -total_amount_currency,
                                'debit': (record.debit - ((record.debit * self.global_discount_rate) / 100)) if total_balance < 0.0 else 0.0,
                                'credit': (record.credit - ((record.credit * self.global_discount_rate) / 100)) if total_balance > 0.0 else 0.0})
                        else:
                            discount = rec.global_discount_rate / len(terms_lines)
                            record.update({
                                'amount_currency': -total_amount_currency,
                                'debit': (record.debit - discount) if total_balance < 0.0 else 0.0,
                                'credit': (record.credit - discount) if total_balance > 0.0 else 0.0
                            })
            if not already_exists and rec.global_discount_rate > 0:
                in_draft_mode = self != self._origin
                if not in_draft_mode and rec.move_type == 'out_invoice':
                    rec._recompute_discount_lines()
                print()

    @api.onchange('global_discount_rate', 'global_discount_type', 'line_ids')
    def _recompute_discount_lines(self):
        """This Function Create The General Entries for Universal Discount"""
        for rec in self:
            type_list = ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']
            if rec.global_discount_rate > 0 and rec.move_type in type_list:
                if rec.is_invoice(include_receipts=True):
                    in_draft_mode = self != self._origin
                    dis_name = "Universal Discount "
                    if rec.global_discount_type == "amount":
                        ks_value = "of amount #" + str(self.global_discount_rate)
                    elif rec.global_discount_type == "percent":
                        ks_value = " @" + str(self.global_discount_rate) + "%"
                    else:
                        ks_value = ''
                    dis_name = dis_name + ks_value
                    terms_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
                    already_exists = self.line_ids.filtered(lambda line: line.name and line.name.find('Universal Discount') == 0)
                    if already_exists:
                        amount = self.amount_discount
                        if self.sales_discount_account_id and (self.move_type == "out_invoice" or self.move_type == "out_refund"):
                            if self.move_type == "out_invoice":
                                already_exists.update({
                                    'name': dis_name,
                                    'debit': amount > 0.0 and amount or 0.0,
                                    'credit': amount < 0.0 and -amount or 0.0,
                                })
                            else:
                                already_exists.update({
                                    'name': dis_name,
                                    'debit': amount < 0.0 and -amount or 0.0,
                                    'credit': amount > 0.0 and amount or 0.0,
                                })
                        if self.purchase_discount_account_id and (self.move_type == "in_invoice" or self.move_type == "in_refund"):
                            if self.move_type == "in_invoice":
                                already_exists.update({
                                    'name': dis_name,
                                    'debit': amount < 0.0 and -amount or 0.0,
                                    'credit': amount > 0.0 and amount or 0.0,
                                })
                            else:
                                already_exists.update({
                                    'name': dis_name,
                                    'debit': amount > 0.0 and amount or 0.0,
                                    'credit': amount < 0.0 and -amount or 0.0,
                                })
                    else:
                        # new_tax_line = self.env['account.move.line']
                        create_method = in_draft_mode and self.env['account.move.line'].new or self.env['account.move.line'].create

                        if self.sales_discount_account_id and (self.move_type == "out_invoice" or self.move_type == "out_refund"):
                            amount = self.amount_discount
                            dict = {
                                'move_name': self.name,
                                'name': dis_name,
                                'price_unit': self.amount_discount,
                                'quantity': 1,
                                'debit': amount < 0.0 and -amount or 0.0,
                                'credit': amount > 0.0 and amount or 0.0,
                                'account_id': self.sales_discount_account_id,
                                'move_id': self._origin,
                                'date': self.date,
                                'exclude_from_invoice_tab': True,
                                'partner_id': terms_lines.partner_id.id,
                                'company_id': terms_lines.company_id.id,
                                'company_currency_id': terms_lines.company_currency_id.id,
                            }
                            if self.move_type == "out_invoice":
                                dict.update({
                                    'debit': amount > 0.0 and amount or 0.0,
                                    'credit': amount < 0.0 and -amount or 0.0,
                                })
                            else:
                                dict.update({
                                    'debit': amount < 0.0 and -amount or 0.0,
                                    'credit': amount > 0.0 and amount or 0.0,
                                })
                            if in_draft_mode:
                                self.line_ids += create_method(dict)
                                # Updation of Invoice Line Id
                                duplicate_id = self.invoice_line_ids.filtered(lambda line: line.name and line.name.find('Universal Discount') == 0)
                                self.invoice_line_ids = self.invoice_line_ids - duplicate_id
                            else:
                                dict.update({
                                    'price_unit': 0.0,
                                    'debit': 0.0,
                                    'credit': 0.0,
                                })
                                self.line_ids = [(0, 0, dict)]

                        if self.purchase_discount_account_id and (self.move_type == "in_invoice" or self.move_type == "in_refund"):
                            amount = self.amount_discount
                            dict = {
                                'move_name': self.name,
                                'name': dis_name,
                                'price_unit': self.amount_discount,
                                'quantity': 1,
                                'debit': amount > 0.0 and amount or 0.0,
                                'credit': amount < 0.0 and -amount or 0.0,
                                'account_id': self.purchase_discount_account_id,
                                'move_id': self.id,
                                'date': self.date,
                                'exclude_from_invoice_tab': True,
                                'partner_id': terms_lines.partner_id.id,
                                'company_id': terms_lines.company_id.id,
                                'company_currency_id': terms_lines.company_currency_id.id,
                            }

                            if self.move_type == "in_invoice":
                                dict.update({
                                    'debit': amount < 0.0 and -amount or 0.0,
                                    'credit': amount > 0.0 and amount or 0.0,
                                })
                            else:
                                dict.update({
                                    'debit': amount > 0.0 and amount or 0.0,
                                    'credit': amount < 0.0 and -amount or 0.0,
                                })
                            self.line_ids += create_method(dict)
                            # updation of invoice line id
                            duplicate_id = self.invoice_line_ids.filtered(lambda line: line.name and line.name.find('Universal Discount') == 0)
                            self.invoice_line_ids = self.invoice_line_ids - duplicate_id

                    amount = self.amount_discount
                    if in_draft_mode:
                        # Update the payement account amount
                        terms_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
                        other_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
                        total_balance = sum(other_lines.mapped('balance'))
                        total_amount_currency = sum(other_lines.mapped('amount_currency'))
                        for record in terms_lines:
                            if rec.global_discount_type == "percent":
                                record.update({
                                    'amount_currency': -total_amount_currency,
                                    'debit': -(record.price_total - ((record.price_total * rec.global_discount_rate) / 100)) if total_balance < 0.0 else 0.0,
                                    'credit': record.price_total - ((record.price_total * rec.global_discount_rate) / 100) if total_balance > 0.0 else 0.0
                                })
                            elif rec.global_discount_type == "amount":
                                discount = rec.global_discount_rate / len(terms_lines)
                                record.update({
                                    'amount_currency': -total_amount_currency,
                                    'debit': -(record.price_total + discount) if total_balance < 0.0 else 0.0,
                                    'credit': record.price_total + discount if total_balance > 0.0 else 0.0
                                })
                    else:
                        terms_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
                        other_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
                        already_exists = self.line_ids.filtered(lambda line: line.name and line.name.find('Universal Discount') == 0)
                        total_balance = sum(other_lines.mapped('balance')) + amount
                        total_amount_currency = sum(other_lines.mapped('amount_currency'))
                        line_ids = []
                        dict1 = {
                            'debit': amount > 0.0 and amount or 0.0,
                            'credit': amount < 0.0 and -amount or 0.0,
                        }
                        line_ids.append((1, already_exists.id, dict1))
                        dict2 = {
                            'debit': total_balance < 0.0 and -total_balance or 0.0,
                            'credit': total_balance > 0.0 and total_balance or 0.0,
                        }
                        for record in terms_lines:
                            if rec.global_discount_type == "percent":
                                dict2 = {
                                    'amount_currency': -total_amount_currency,
                                    'debit': -(record.price_total - ((
                                                                             record.price_total * rec.global_discount_rate) / 100)) if total_balance < 0.0 else 0.0,
                                    'credit': record.price_total - ((
                                                                            record.price_total * rec.global_discount_rate) / 100) if total_balance > 0.0 else 0.0
                                }
                            elif rec.global_discount_type == "amount":
                                discount = rec.global_discount_rate / len(terms_lines)
                                dict2 = {
                                    'amount_currency': -total_amount_currency,
                                    'debit': -(
                                            record.price_total + discount) if total_balance < 0.0 else 0.0,
                                    'credit': record.price_total + discount if total_balance > 0.0 else 0.0
                                }
                            line_ids.append((1, record.id, dict2))
                        # self.line_ids = [(1, already_exists.id, dict1), (1, terms_lines.id, dict2)]
                        self.line_ids = line_ids

            elif self.global_discount_rate <= 0:
                already_exists = self.line_ids.filtered(lambda line: line.name and line.name.find('Universal Discount') == 0)
                if already_exists:
                    self.line_ids -= already_exists
                    terms_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
                    other_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
                    total_balance = sum(other_lines.mapped('balance'))
                    total_amount_currency = sum(other_lines.mapped('amount_currency'))
                    terms_lines.update({
                        'amount_currency': -total_amount_currency,
                        'debit': total_balance < 0.0 and -total_balance or 0.0,
                        'credit': total_balance > 0.0 and total_balance or 0.0,
                    })

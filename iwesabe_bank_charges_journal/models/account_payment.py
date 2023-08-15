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

from openerp import models, fields, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _synchronize_business_models(self, changed_fields):
        for rec in self:
            if self._context.get('skip_account_move_synchronization'):
                return
            self_sudo = rec.sudo()
            if self_sudo.payment_id.bank_charge > 1:
                self_sudo.payment_id.with_context(skip_account_move_synchronization=True)._synchronize_from_moves(
                    changed_fields)
                self_sudo.statement_line_id.with_context(skip_account_move_synchronization=True)._synchronize_from_moves(changed_fields)
            else:
                self_sudo.payment_id._synchronize_from_moves(changed_fields)
                self_sudo.statement_line_id._synchronize_from_moves(changed_fields)


class account_journal(models.Model):
    _inherit = "account.journal"

    apply_charges = fields.Boolean("Apply Charges")
    # fees_amount = fields.Float("Amount")
    fees_amount = fields.Float("Amount", digits=(16, 5))
    fees_type = fields.Selection(selection=[('fixed', 'Fixed'), ('percentage', 'Percentage')], string="Type", default="fixed")
    optional = fields.Boolean("Optional")
    default_card_account_id = fields.Many2one('account.account', 'Default Bank Charge Account')
    default_tax_account_id = fields.Many2one('account.account', 'Default Tax Account')


class account_payment(models.Model):
    _inherit = "account.payment"

    @api.onchange('journal_id', 'amount', 'partner_id', 'is_bank_charge')
    def onchange_bank_charge(self):
        if self.is_bank_charge:
            if self.journal_id.fees_type == 'fixed':
                self.bank_charge = self.journal_id.fees_amount
            if self.journal_id.fees_type == 'percentage':
                percentage = self.journal_id.fees_amount
                bank_charges = (percentage*self.amount)/100
                self.bank_charge = bank_charges

    @api.depends('journal_id')
    def get_journal_type(self):
        if self.journal_id:
            if self.journal_id.type == 'bank':
                self.is_journal_bank = True
            else:
                self.is_journal_bank = False
        else:
            self.is_journal_bank = False

    is_journal_bank = fields.Boolean(string="", compute='get_journal_type')
    bank_charge = fields.Float('Bank charges (Untaxed)', default=0.00)
    bank_tax_id = fields.Many2one(comodel_name="account.tax", string="Bank Charge Tax", required=False, )
    is_bank_charge = fields.Boolean(string="Bank Charges",)

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        ''' Prepare the dictionary to create the default account.move.lines for the current payment.
        :param write_off_line_vals: Optional dictionary to create a write-off account.move.line easily containing:
            * amount:       The amount to be added to the counterpart amount.
            * name:         The label to set on the line.
            * account_id:   The account on which create the write-off.
        :return: A list of python dictionary to be passed to the account.move.line's 'create' method.
        '''
        self.ensure_one()
        write_off_line_vals = write_off_line_vals or {}

        if not self.journal_id.payment_debit_account_id or not self.journal_id.payment_credit_account_id:
            raise UserError(_(
                "You can't create a new payment without an outstanding payments/receipts account set on the %s journal.",
                self.journal_id.display_name))

        # Compute amounts.
        write_off_amount = write_off_line_vals.get('amount', 0.0)

        if self.payment_type == 'inbound':
            # Receive money.
            counterpart_amount = -self.amount
            write_off_amount *= -1
        elif self.payment_type == 'outbound':
            # Send money.
            counterpart_amount = self.amount
        else:
            counterpart_amount = 0.0
            write_off_amount = 0.0

        balance = self.currency_id._convert(counterpart_amount, self.company_id.currency_id, self.company_id, self.date)
        counterpart_amount_currency = counterpart_amount
        write_off_balance = self.currency_id._convert(write_off_amount, self.company_id.currency_id, self.company_id,
                                                      self.date)
        write_off_amount_currency = write_off_amount
        currency_id = self.currency_id.id

        if self.is_internal_transfer:
            if self.payment_type == 'inbound':
                liquidity_line_name = _('Transfer to %s', self.journal_id.name)
            else:  # payment.payment_type == 'outbound':
                liquidity_line_name = _('Transfer from %s', self.journal_id.name)
        else:
            liquidity_line_name = self.payment_reference

        # Compute a default label to set on the journal items.

        payment_display_name = {
            'outbound-customer': _("Customer Reimbursement"),
            'inbound-customer': _("Customer Payment"),
            'outbound-supplier': _("Vendor Payment"),
            'inbound-supplier': _("Vendor Reimbursement"),
        }

        default_line_name = self.env['account.move.line']._get_default_line_name(
            payment_display_name['%s-%s' % (self.payment_type, self.partner_type)],
            self.amount,
            self.currency_id,
            self.date,
            partner=self.partner_id,
        )

        line_vals_list = [
            # Liquidity line.
            {
                'name': liquidity_line_name or default_line_name,
                'date_maturity': self.date,
                'amount_currency': -counterpart_amount_currency,
                'currency_id': currency_id,
                'debit': balance < 0.0 and -balance or 0.0,
                'credit': balance > 0.0 and balance or 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.journal_id.payment_debit_account_id.id if balance < 0.0 else self.journal_id.payment_credit_account_id.id,
            },
            # Receivable / Payable.
            {
                'name': self.payment_reference or default_line_name,
                'date_maturity': self.date,
                'amount_currency': counterpart_amount_currency + write_off_amount_currency if currency_id else 0.0,
                'currency_id': currency_id,
                'debit': balance + write_off_balance > 0.0 and balance + write_off_balance or 0.0,
                'credit': balance + write_off_balance < 0.0 and -balance - write_off_balance or 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.destination_account_id.id,
            },
        ]
        if write_off_balance:
            # Write-off line.
            line_vals_list.append({
                'name': write_off_line_vals.get('name') or default_line_name,
                'amount_currency': -write_off_amount_currency,
                'currency_id': currency_id,
                'debit': write_off_balance < 0.0 and -write_off_balance or 0.0,
                'credit': write_off_balance > 0.0 and write_off_balance or 0.0,
                'partner_id': self.partner_id.id,
                'account_id': write_off_line_vals.get('account_id'),
            })

        if self.is_bank_charge:
            bank_charges_bank_account = 0.0
            if self.bank_charge:
                bank_charges_bank_account = self.bank_charge
            else:
                if self.journal_id.fees_type == 'fixed':
                    bank_charges_bank_account = self.journal_id.fees_amount
                if self.journal_id.fees_type == 'percentage':
                    percentage = self.journal_id.fees_amount
                    bank_charges_bank_account = (percentage * self.amount) / 100

            bank_charges_tax_account = 0.0
            if self.bank_tax_id and bank_charges_bank_account:
                if self.bank_tax_id.amount_type == 'percent':
                    bank_charges_tax_account = bank_charges_bank_account * (self.bank_tax_id.amount / 100)
                elif self.bank_tax_id.amount_type == 'fixed':
                    bank_charges_tax_account = self.bank_tax_id.amount

            if not self.journal_id.default_tax_account_id:
                raise UserError(str('Please configure Default Tax Account'))
            if not self.journal_id.default_card_account_id:
                raise UserError(str('Please configure Default Bank Charge Account for %s' % self.journal_id.name))

        if self.journal_id.apply_charges and self.is_bank_charge:
            line_vals_list.append({'debit': bank_charges_bank_account,
                                   'name': _('Bank charge: %s') % self.name,
                                   # 'payment_id': self.id,
                                   'partner_id': self.partner_id.id,
                                   'currency_id': self.currency_id.id,
                                   # 'move_id': move.id,
                                   'account_id': self.journal_id.default_card_account_id.id})

            # aml_obj.create(bank_line_values)

            line_vals_list.append({'debit': bank_charges_tax_account,
                                   'name': _('Tax for Bank charge: %s') % self.name,
                                   # 'payment_id': self.id,
                                   'partner_id': self.partner_id.id,
                                   'currency_id': self.currency_id.id,
                                   # 'move_id': move.id,
                                   'account_id': self.journal_id.default_tax_account_id.id})
            # aml_obj.create(bank_line_tax_values)
            line_vals_list.append({'credit': bank_charges_bank_account + bank_charges_tax_account,
                                   'name': _('Bank charge: %s') % self.name,
                                   # 'payment_id': self.id,
                                   'partner_id': self.partner_id.id,
                                   'currency_id': self.currency_id.id,
                                   # 'move_id': move.id,
                                   'account_id': self.journal_id.payment_debit_account_id.id})
            # aml_obj.create(bank_line_values_debit)

        return line_vals_list


class account_register_payments(models.TransientModel):
    _inherit = "account.payment.register"

    bank_charge = fields.Float('Bank charges (Untaxed)', default=0.00)
    bank_tax_id = fields.Many2one(comodel_name="account.tax", string="Bank Charge Tax", required=False, )
    is_bank_charge = fields.Boolean(string="Bank Charges", )
    is_journal_bank = fields.Boolean(string="", compute='get_journal_type')

    @api.depends('journal_id')
    def get_journal_type(self):
        if self.journal_id:
            if self.journal_id.type == 'bank':
                self.is_journal_bank = True
            else:
                self.is_journal_bank = False
        else:
            self.is_journal_bank = False

    @api.onchange('journal_id', 'amount', 'partner_id', 'is_bank_charge')
    def onchange_bank_charge(self):
        if self.is_bank_charge:
            if self.journal_id.fees_type == 'fixed':
                self.bank_charge = self.journal_id.fees_amount
            if self.journal_id.fees_type == 'percentage':
                percentage = self.journal_id.fees_amount
                bank_charges = (percentage * self.amount) / 100
                self.bank_charge = bank_charges

    def _create_payment_vals_from_wizard(self):
        res = super(account_register_payments, self)._create_payment_vals_from_wizard()
        res.update({'bank_charge': self.bank_charge, 'bank_tax_id': self.bank_tax_id.id, 'is_bank_charge': self.is_bank_charge})
        return res

    def _create_payment_vals_from_batch(self, batch_result):
        res = super(account_register_payments, self)._create_payment_vals_from_batch(batch_result)
        res.update({'bank_charge': self.bank_charge, 'bank_tax_id': self.bank_tax_id.id,
                    'is_bank_charge': self.is_bank_charge})
        return res

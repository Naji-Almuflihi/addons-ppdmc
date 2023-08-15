# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, exceptions
from odoo.exceptions import UserError


class account_payment(models.Model):
    _inherit = "account.payment"

    internal_transfer_type = fields.Selection([('a_to_a', 'Account To Account'), ('j_to_j', 'Journal To Journal'), ('j_to_a', 'Journal To Account'), ('a_to_j', 'Account To Journal')], string=' Internal Transfer Type', default='a_to_a')
    from_account_id = fields.Many2one('account.account', string="From Account")
    to_account_id = fields.Many2one('account.account', string="To Account")
    to_journal_id = fields.Many2one('account.journal', string="To Journal")
    from_journal_id = fields.Many2one('account.journal', string="From Journal")

    def write(self, vals):
        # OVERRIDE
        res = super().write(vals)
        for rec in self:
            rec._synchronize_to_moves(set(vals.keys()))
        return res

    def _synchronize_to_moves(self, changed_fields):
        ''' Update the account.move regarding the modified account.payment.
        :param changed_fields: A list containing all modified fields on account.payment.
        '''
        for rec in self:
            if rec.is_bank_charge:
                if rec._context.get('skip_account_move_synchronization'):
                    return

                if not any(field_name in changed_fields for field_name in (
                        'date', 'amount', 'payment_type', 'partner_type', 'payment_reference', 'is_internal_transfer',
                        'currency_id', 'partner_id', 'destination_account_id', 'partner_bank_id', 'bank_charge',
                        'bank_tax_id', 'is_bank_charge'
                )):
                    return

                for pay in rec.with_context(skip_account_move_synchronization=True):
                    liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()

                    # Make sure to preserve the write-off amount.
                    # This allows to create a new payment with custom 'line_ids'.

                    if writeoff_lines:
                        writeoff_amount = sum(writeoff_lines.mapped('amount_currency'))
                        counterpart_amount = counterpart_lines['amount_currency']
                        if writeoff_amount > 0.0 and counterpart_amount > 0.0:
                            sign = 1
                        else:
                            sign = -1

                        write_off_line_vals = {
                            'name': writeoff_lines[0].name,
                            'amount': writeoff_amount * sign,
                            'account_id': writeoff_lines[0].account_id.id,
                        }
                    else:
                        write_off_line_vals = {}

                    line_vals_list = pay._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)
                    line_ids_commands = [
                        (1, liquidity_lines.id, line_vals_list[0]),
                        (1, counterpart_lines.id, line_vals_list[1]),
                    ]

                    for line in writeoff_lines:
                        line_ids_commands.append((2, line.id))
                    if len(line_vals_list) == 4:
                        if writeoff_lines:
                            line_ids_commands.append((0, 0, line_vals_list[2]))
                            line_ids_commands.append((0, 0, line_vals_list[3]))
                    if len(line_vals_list) == 5:
                        if writeoff_lines:
                            line_ids_commands.append((0, 0, line_vals_list[2]))
                            line_ids_commands.append((0, 0, line_vals_list[3]))
                            line_ids_commands.append((0, 0, line_vals_list[4]))
                    else:
                        if writeoff_lines:
                            line_ids_commands.append((0, 0, line_vals_list[2]))

                    # Update the existing journal items.
                    # If dealing with multiple write-off lines, they are dropped and a new one is generated.

                    pay.move_id.write({
                        'partner_id': pay.partner_id.id,
                        'currency_id': pay.currency_id.id,
                        'partner_bank_id': pay.partner_bank_id.id,
                        'line_ids': line_ids_commands,
                    })
            elif rec.is_internal_transfer:
                if rec._context.get('skip_account_move_synchronization'):
                    return

                if not any(field_name in changed_fields for field_name in (
                        'date', 'amount', 'payment_type', 'partner_type', 'payment_reference', 'is_internal_transfer',
                        'currency_id', 'partner_id', 'destination_account_id', 'partner_bank_id', 'from_account_id', 'to_account_id', 'to_journal_id', 'from_journal_id'
                )):
                    return

                for pay in rec.with_context(skip_account_move_synchronization=True):
                    liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()

                    # Make sure to preserve the write-off amount.
                    # This allows to create a new payment with custom 'line_ids'.

                    if writeoff_lines:
                        writeoff_amount = sum(writeoff_lines.mapped('amount_currency'))
                        counterpart_amount = counterpart_lines['amount_currency']
                        if writeoff_amount > 0.0 and counterpart_amount > 0.0:
                            sign = 1
                        else:
                            sign = -1

                        write_off_line_vals = {
                            'name': writeoff_lines[0].name,
                            'amount': writeoff_amount * sign,
                            'account_id': writeoff_lines[0].account_id.id,
                        }
                    else:
                        write_off_line_vals = {}

                    line_vals_list = pay._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)
                    if len(counterpart_lines) > 1 or len(liquidity_lines) > 1 and self.is_internal_transfer:
                        raise exceptions.ValidationError(
                            'You can not edit in this payment that have internal transfer, you must create new one. by pressing on discard button and then delete this payment , then you can create new one or contact to your administrator.')

                    line_ids_commands = [
                        (1, liquidity_lines.id, line_vals_list[0]),
                        (1, counterpart_lines.id, line_vals_list[1]),
                    ]

                    for line in writeoff_lines:
                        line_ids_commands.append((2, line.id))

                    if writeoff_lines:
                        line_ids_commands.append((0, 0, line_vals_list[2]))

                    # Update the existing journal items.
                    # If dealing with multiple write-off lines, they are dropped and a new one is generated.

                    pay.move_id.write({
                        'partner_id': pay.partner_id.id,
                        'currency_id': pay.currency_id.id,
                        'partner_bank_id': pay.partner_bank_id.id,
                        'line_ids': line_ids_commands,
                    })
            else:
                return super(account_payment, self)._synchronize_to_moves(changed_fields)

    @api.onchange('is_internal_transfer')
    def check_internal_and_bank_journal(self):
        if self.is_internal_transfer:
            self.is_bank_charge = False
            self.bank_charge = 0.0
            self.bank_tax_id = False

    # @api.depends('destination_account_id', 'journal_id')
    # def _compute_is_internal_transfer(self):
    #     for payment in self:
    #         # is_partner_ok = payment.partner_id
    #         is_account_ok = payment.destination_account_id or payment.journal_id.company_id.transfer_account_id
    #         # payment.is_internal_transfer = is_partner_ok and is_account_ok

    @api.onchange('journal_id', 'internal_transfer_type', 'is_internal_transfer')
    def _onchange_journal(self):
        # payment_account_list = []
        if self.is_internal_transfer and self.internal_transfer_type in ['a_to_a', 'a_to_j']:
            account_ids = self.env['account.account'].search([('internal_type', 'in', ('receivable', 'payable', 'liquidity', 'other'))])
            if account_ids:
                return {'domain': {'from_account_id': [('id', 'in', account_ids.ids)]}}
        return {}

    @api.depends('journal_id', 'partner_id', 'partner_type', 'is_internal_transfer', 'internal_transfer_type', 'to_account_id', 'to_journal_id')
    def _compute_destination_account_id(self):
        self.destination_account_id = False
        for pay in self:
            if pay.is_internal_transfer:
                pay.destination_account_id = pay.journal_id.company_id.transfer_account_id
                # Custom Code
                if pay.internal_transfer_type == 'a_to_a':
                    pay.destination_account_id = pay.to_account_id

                if pay.internal_transfer_type == 'a_to_j':
                    pay.destination_account_id = pay.to_journal_id.payment_debit_account_id or pay.journal_id.company_id.transfer_account_id

                if pay.internal_transfer_type == 'j_to_a':
                    pay.destination_account_id = pay.to_account_id

                if pay.internal_transfer_type == 'j_to_j':
                    pay.destination_account_id = pay.to_journal_id.payment_debit_account_id or pay.journal_id.company_id.transfer_account_id

            elif pay.partner_type == 'customer':
                # Receive money from invoice or send money to refund it.
                if pay.partner_id:
                    pay.destination_account_id = pay.partner_id.with_company(pay.company_id).property_account_receivable_id
                else:
                    pay.destination_account_id = self.env['account.account'].search([
                        ('company_id', '=', pay.company_id.id),
                        ('internal_type', '=', 'receivable'),
                    ], limit=1)
            elif pay.partner_type == 'supplier':
                # Send money to pay a bill or receive money to refund it.
                if pay.partner_id:
                    pay.destination_account_id = pay.partner_id.with_company(pay.company_id).property_account_payable_id
                else:
                    pay.destination_account_id = self.env['account.account'].search([
                        ('company_id', '=', pay.company_id.id),
                        ('internal_type', '=', 'payable'),
                    ], limit=1)

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        ''' Prepare the dictionary to create the default account.move.lines for the current payment.
        :param write_off_line_vals: Optional dictionary to create a write-off account.move.line easily containing:
            * amount:       The amount to be added to the counterpart amount.
            * name:         The label to set on the line.
            * account_id:   The account on which create the write-off.
        :return: A list of python dictionary to be passed to the account.move.line's 'create' method.
        '''
        for rec in self:
            rec.ensure_one()
            write_off_line_vals = write_off_line_vals or {}

            if not rec.journal_id.payment_debit_account_id or not rec.journal_id.payment_credit_account_id:
                raise UserError(_(
                    "You can't create a new payment without an outstanding payments/receipts account set on the %s journal.",
                    rec.journal_id.display_name))

            # Compute amounts.
            write_off_amount = write_off_line_vals.get('amount', 0.0)

            if rec.payment_type == 'inbound':
                # Receive money.
                counterpart_amount = -rec.amount
                write_off_amount *= -1
            elif rec.payment_type == 'outbound':
                # Send money.
                counterpart_amount = rec.amount
            else:
                counterpart_amount = 0.0
                write_off_amount = 0.0

            balance = rec.currency_id._convert(counterpart_amount, rec.company_id.currency_id, rec.company_id, rec.date)
            counterpart_amount_currency = counterpart_amount
            write_off_balance = rec.currency_id._convert(write_off_amount, rec.company_id.currency_id, rec.company_id, rec.date)
            write_off_amount_currency = write_off_amount
            currency_id = rec.currency_id.id

            if rec.is_internal_transfer:
                if rec.payment_type == 'inbound':
                    liquidity_line_name = _('Transfer to %s', rec.journal_id.name)
                else:  # payment.payment_type == 'outbound':
                    liquidity_line_name = _('Transfer from %s', rec.journal_id.name)
            else:
                liquidity_line_name = rec.payment_reference

            # Compute a default label to set on the journal items.

            payment_display_name = {
                'outbound-customer': _("Customer Reimbursement"),
                'inbound-customer': _("Customer Payment"),
                'outbound-supplier': _("Vendor Payment"),
                'inbound-supplier': _("Vendor Reimbursement"),
            }

            default_line_name = self.env['account.move.line']._get_default_line_name(
                payment_display_name['%s-%s' % (rec.payment_type, rec.partner_type)],
                rec.amount,
                rec.currency_id,
                rec.date,
                partner=rec.partner_id,
            )

            liquidity_line_account = rec.journal_id.payment_debit_account_id.id if balance < 0.0 else rec.journal_id.payment_credit_account_id.id

            # Custom Code
            if rec.is_internal_transfer and rec.internal_transfer_type == 'a_to_a':
                liquidity_line_account = rec.from_account_id.id

            if rec.is_internal_transfer and rec.internal_transfer_type == 'a_to_j':
                liquidity_line_account = rec.from_account_id.id

            if rec.is_internal_transfer and rec.internal_transfer_type == 'j_to_a':
                liquidity_line_account = rec.from_journal_id.payment_credit_account_id.id

            if rec.is_internal_transfer and rec.internal_transfer_type == 'j_to_j':
                liquidity_line_account = rec.from_journal_id.payment_credit_account_id.id

            line_vals_list = [
                # Liquidity line.
                {
                    'name': liquidity_line_name or default_line_name,
                    'date_maturity': rec.date,
                    'amount_currency': -counterpart_amount_currency,
                    'currency_id': currency_id,
                    'debit': balance < 0.0 and -balance or 0.0,
                    'credit': balance > 0.0 and balance or 0.0,
                    'partner_id': rec.partner_id.id,
                    'account_id': liquidity_line_account,
                    'journal_id': rec.from_journal_id.id,
                },
                # Receivable / Payable.
                {
                    'name': rec.payment_reference or default_line_name,
                    'date_maturity': rec.date,
                    'amount_currency': counterpart_amount_currency + write_off_amount_currency if currency_id else 0.0,
                    'currency_id': currency_id,
                    'debit': balance + write_off_balance > 0.0 and balance + write_off_balance or 0.0,
                    'credit': balance + write_off_balance < 0.0 and -balance - write_off_balance or 0.0,
                    'partner_id': rec.partner_id.id,
                    'account_id': rec.destination_account_id.id,
                    'journal_id': rec.to_journal_id.id,
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
                    'partner_id': rec.partner_id.id,
                    'account_id': write_off_line_vals.get('account_id'),
                })

            if rec.is_bank_charge:
                bank_charges_bank_account = 0.0
                if rec.bank_charge:
                    bank_charges_bank_account = rec.bank_charge
                else:
                    if rec.journal_id.fees_type == 'fixed':
                        bank_charges_bank_account = rec.journal_id.fees_amount
                    if rec.journal_id.fees_type == 'percentage':
                        percentage = rec.journal_id.fees_amount
                        bank_charges_bank_account = (percentage * rec.amount) / 100

                bank_charges_tax_account = 0.0
                if rec.bank_tax_id and bank_charges_bank_account:
                    if rec.bank_tax_id.amount_type == 'percent':
                        bank_charges_tax_account = bank_charges_bank_account * (rec.bank_tax_id.amount / 100)
                    elif rec.bank_tax_id.amount_type == 'fixed':
                        bank_charges_tax_account = rec.bank_tax_id.amount

                if not rec.journal_id.default_tax_account_id:
                    raise UserError(str('Please configure Default Tax Account in Journal'))
                if not rec.journal_id.default_card_account_id:
                    raise UserError(str('Please configure Default Bank Charge Account for %s' % rec.journal_id.name))

                if rec.journal_id.apply_charges and rec.is_bank_charge:
                    line_vals_list.append({'debit': bank_charges_bank_account,
                                           'name': _('Bank charge: %s') % rec.name,
                                           # 'payment_id': rec.id,
                                           'partner_id': rec.partner_id.id,
                                           'currency_id': rec.currency_id.id,
                                           # 'move_id': move.id,
                                           'account_id': rec.journal_id.default_card_account_id.id})

                    # aml_obj.create(bank_line_values)

                    if rec.bank_tax_id:
                        line_vals_list.append({'debit': bank_charges_tax_account,
                                               'name': _('Tax for Bank charge: %s') % rec.name,
                                               'partner_id': rec.partner_id.id,
                                               'currency_id': rec.currency_id.id,
                                               'account_id': rec.journal_id.default_tax_account_id.id})
                    # aml_obj.create(bank_line_tax_values)
                    line_vals_list.append({'credit': bank_charges_bank_account + bank_charges_tax_account,
                                           'name': _('Bank charge: %s') % rec.name,
                                           'partner_id': rec.partner_id.id,
                                           'currency_id': rec.currency_id.id,
                                           'account_id': rec.journal_id.payment_credit_account_id.id})

            return line_vals_list

    def _seek_for_lines(self):
        ''' Helper used to dispatch the journal items between:
        - The lines using the temporary liquidity account.
        - The lines using the counterpart account.
        - The lines being the write-off lines.
        :return: (liquidity_lines, counterpart_lines, writeoff_lines)
        '''
        self.ensure_one()

        liquidity_lines = self.env['account.move.line']
        counterpart_lines = self.env['account.move.line']
        writeoff_lines = self.env['account.move.line']
        account_add = []

        if self.is_bank_charge:
            for line in self.move_id.line_ids:

                if line.account_id in (self.journal_id.payment_debit_account_id,
                                       self.journal_id.payment_credit_account_id) and line.account_id.id not in account_add:
                    account_add.append(line.account_id.id)

                    liquidity_lines += line
                elif line.account_id.internal_type in ('receivable', 'payable'):
                    if line.account_id.id not in account_add:
                        account_add.append(line.account_id.id)
                        counterpart_lines += line
                else:
                    writeoff_lines += line

            return liquidity_lines, counterpart_lines, writeoff_lines

        else:
            for line in self.move_id.line_ids:
                if line.account_id in (
                        self.journal_id.default_account_id,
                        self.journal_id.payment_debit_account_id,
                        self.journal_id.payment_credit_account_id,
                ):
                    liquidity_lines += line
                elif line.account_id.internal_type in ('receivable', 'payable', 'liquidity', 'other'):
                    counterpart_lines += line
                else:
                    writeoff_lines += line

            return liquidity_lines, counterpart_lines, writeoff_lines

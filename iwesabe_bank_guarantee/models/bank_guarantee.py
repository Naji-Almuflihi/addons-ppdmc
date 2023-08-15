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

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime as date


class BankGuarantee(models.Model):
    _name = 'bank.guarantee'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'sequence.mixin']

    @api.model
    def _get_default_currency(self):
        user = self.env.user
        return user.company_id.currency_id

    @api.depends('end_date', 'issue_date')
    def _get_guarantee_period(self):
        days=0
        if self.end_date and self.issue_date:
            days = str((self.end_date - self.issue_date).days)
        self.guarantee_period = days

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('bank.guarantee.seq') or '/'
        return super(BankGuarantee, self).create(vals)

    @api.depends('guarantee_rate', 'guarantee_amount','guarantee_expense_amount')
    def _compute_amount(self):
        for line in self:
            guarantee_rate = line.guarantee_rate
            guarantee_amount = line.guarantee_amount
            line.total_amount_guarantee_rate = guarantee_rate*guarantee_amount/100

    name = fields.Char('Sequence',default='New',copy=False)
    guarantee_number = fields.Char('Guarantee Number',copy=False)
    description = fields.Char('Description')
    issue_date = fields.Date('Issue Date')
    end_date = fields.Date('End Date')
    renew_date = fields.Date('Renew Date')
    guarantee_period = fields.Integer('Guarantee Period',compute=_get_guarantee_period)
    guarantee_type = fields.Selection([
        ('basic', 'Basic Guarantee'),
        ('final', 'Final Guarantee')
    ],'Guarantee Type')
    partner_id = fields.Many2one('res.partner','Customer')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=_get_default_currency)
    guarantee_amount = fields.Float('Guarantee Amount')
    guarantee_rate = fields.Integer('Guarantee Rate')
    guarantee_expense_amount = fields.Integer('Guarantee Expense Amount')
    tax_id = fields.Many2one('account.tax','VAT')
    journal_id = fields.Many2one('account.journal','Bank Name',domain="[('type', 'in', ['bank','cash'])]")
    expense_account_id = fields.Many2one('account.account','Guarantee Expense Account')
    guarantee_account_id = fields.Many2one('account.account','Guarantee Account')
    note = fields.Text('Note')
    total_amount_guarantee_rate = fields.Monetary('Guarantee Rate Total',compute='_compute_amount')
    total_amount_guarantee = fields.Float('Guarantee Total Amount')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('repaid', 'Repaid'),
        ('end', 'End')
    ], 'status',default='draft',tracking=True)

    move_ids = fields.One2many('account.move','guarantee_id',string='Journal Entries')
    move_count = fields.Integer('Entries', compute='_compute_move_count')
    is_customer = fields.Boolean('is customer')
    amount_currency_id = fields.Many2one('res.currency', string='Currency')

    @api.depends('move_ids')
    def _compute_move_count(self):
        for move in self:
            move.move_count = len(move.move_ids)

    def action_view_journal(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_journal_line")
        action['domain'] = [('id', 'in', self.mapped('move_ids.id'))]
        action['context'] = dict(self._context, create=False)
        return action

    def action_confirm(self):
        self.state = 'approved'

    def action_paid(self):
        self.state = 'paid'
        lines = []
        if self.journal_id:
            tax_amount = self.guarantee_expense_amount*(self.tax_id.amount/100)
            total_amount = tax_amount+self.guarantee_expense_amount+self.total_amount_guarantee_rate
            guarantee_total_amount = {
                'credit': total_amount,
                'name': self.journal_id.name+'/'+self.partner_id.name,
                'partner_id': self.partner_id.id,
                'currency_id': self.currency_id.id,
                'account_id': self.journal_id.default_account_id.id
            }
            lines.append((0, 0,guarantee_total_amount))
            guarantee_amount = {
                'debit': self.total_amount_guarantee_rate,
                'name': str(self.description) + '/' + str(self.name),
                'partner_id': self.partner_id.id,
                'currency_id': self.currency_id.id,
                'account_id': self.guarantee_account_id.id
            }
            lines.append((0, 0,guarantee_amount))
            guarantee_amount_exp = {'debit': self.guarantee_expense_amount,
                                    'partner_id': self.partner_id.id,
                                    'currency_id': self.currency_id.id,
                                    'account_id': self.expense_account_id.id
                                    }
            lines.append((0, 0,guarantee_amount_exp))
            guarantee_amount_tax = {'debit': tax_amount,
                                    'name': self.tax_id.name,
                                    'partner_id': self.partner_id.id,
                                    'currency_id': self.currency_id.id,
                                    'account_id': self.tax_id.mapped('invoice_repartition_line_ids.account_id').id
                                    }
            lines.append((0, 0,guarantee_amount_tax))
            vals = {
                'guarantee_id': self.id,
                'partner_id': self.partner_id.id,
                'payment_reference': self.name,
                'invoice_date': self.issue_date,
                'journal_id': self.journal_id.id,
                'line_ids':lines
            }
            move = self.env['account.move'].create(vals)
            move.post()

    def action_repaid_guarantee(self):
        lines=[]
        for guarantee_id in self:
            guarantee_id.state = 'repaid'
            if guarantee_id.journal_id:
                total_amount = guarantee_id.total_amount_guarantee_rate
                guarantee_total_amount_c = {
                    'credit': total_amount,
                    'name': str(guarantee_id.description) + str(guarantee_id.name),
                    'partner_id': guarantee_id.partner_id.id,
                    'currency_id': guarantee_id.currency_id.id,
                    'account_id': guarantee_id.guarantee_account_id.id
                }
                lines.append((0, 0, guarantee_total_amount_c))
                guarantee_amount_d = {
                    'debit': guarantee_id.total_amount_guarantee_rate,
                    'name': guarantee_id.journal_id.name+'/'+guarantee_id.partner_id.name,
                    'partner_id': guarantee_id.partner_id.id,
                    'currency_id': guarantee_id.currency_id.id,
                    'account_id':guarantee_id.journal_id.default_account_id.id
                }
                lines.append((0, 0, guarantee_amount_d))
                vals = {
                    'guarantee_id': guarantee_id.id,
                    'partner_id': guarantee_id.partner_id.id,
                    'payment_reference': guarantee_id.name,
                    'invoice_date': guarantee_id.issue_date,
                    'journal_id': guarantee_id.journal_id.id,
                    'line_ids': lines
                }
                move = self.env['account.move'].create(vals)
                move.post()


    def action_renew(self):
        return {
            'name': "Renew/End Bank Guarantee ",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'bank.guarantee.renew',
            'view_id': self.env.ref('iwesabe_bank_guarantee.view_bank_guarantee_wizard').id,
            'target': 'new',
            'context':{'default_end_date':self.end_date}
        }


class BankGuaranteeRenew(models.TransientModel):
    _name = 'bank.guarantee.renew'

    end_date = fields.Date('End Date')
    guarantee_expense_amount = fields.Integer('Guarantee Expense Amount')

    def action_end_guarantee(self):
        guarantee = self.env.context.get('active_id')
        guarantee_id = self.env['bank.guarantee'].browse(guarantee)
        guarantee_id.state = 'end'

    def action_renew_guarantee(self):
        guarantee = self.env.context.get('active_id')
        guarantee_id = self.env['bank.guarantee'].browse(guarantee)
        guarantee_id.state = 'paid'
        if self.guarantee_expense_amount:
            guarantee_id.guarantee_expense_amount = self.guarantee_expense_amount
        lines = []
        if guarantee_id.journal_id:
            expense_amount = guarantee_id.guarantee_expense_amount
            guarantee_total_amount_d = {
                'debit': guarantee_id.guarantee_expense_amount,
                'partner_id': guarantee_id.partner_id.id,
                'currency_id': guarantee_id.currency_id.id,
                'account_id': guarantee_id.guarantee_account_id.id
            }
            lines.append((0, 0, guarantee_total_amount_d))
            tax_amount = guarantee_id.guarantee_expense_amount*(guarantee_id.tax_id.amount/100)
            guarantee_amount_tax_d = {'debit': tax_amount,
                                      'name': guarantee_id.tax_id.name,
                                      'partner_id': guarantee_id.partner_id.id,
                                      'currency_id': guarantee_id.currency_id.id,
                                      'account_id': guarantee_id.tax_id.mapped('invoice_repartition_line_ids.account_id').id
                                      }
            lines.append((0, 0, guarantee_amount_tax_d))

            guarantee_amount_c = {
                'credit': guarantee_id.guarantee_expense_amount+tax_amount,
                'name': guarantee_id.journal_id.name+'/'+guarantee_id.partner_id.name,
                'partner_id': guarantee_id.partner_id.id,
                'currency_id': guarantee_id.currency_id.id,
                'account_id': guarantee_id.journal_id.default_account_id.id
            }
            lines.append((0, 0, guarantee_amount_c))

            vals = {
                'guarantee_id':guarantee_id.id,
                'partner_id': guarantee_id.partner_id.id,
                'payment_reference': guarantee_id.name,
                'invoice_date': guarantee_id.issue_date,
                'journal_id': guarantee_id.journal_id.id,
                'line_ids': lines
            }
            move = self.env['account.move'].create(vals)
            move.post()



class AccountMove(models.Model):
    _inherit = 'account.move'

    guarantee_id = fields.Many2one('bank.guarantee','guarantee')















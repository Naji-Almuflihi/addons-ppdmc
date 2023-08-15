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
from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    payment_debit_account_id = fields.Many2one(
        'account.account', check_company=True, copy=False, ondelete='restrict',
        help="Incoming payments entries triggered by invoices/refunds will be posted on the Outstanding Receipts Account "
             "and displayed as blue lines in the bank reconciliation widget. During the reconciliation process, concerned "
             "transactions will be reconciled with entries on the Outstanding Receipts Account instead of the "
             "receivable account.", string='Outstanding Receipts Account',
        domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id), \
                                 ('user_type_id.type', 'not in', ('receivable', 'payable'))]")
    payment_credit_account_id = fields.Many2one(
        'account.account', check_company=True, copy=False, ondelete='restrict',
        help="Outgoing payments entries triggered by bills/credit notes will be posted on the Outstanding Payments Account "
             "and displayed as blue lines in the bank reconciliation widget. During the reconciliation process, concerned "
             "transactions will be reconciled with entries on the Outstanding Payments Account instead of the "
             "payable account.", string='Outstanding Payments Account',
        domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id), \
                                 ('user_type_id.type', 'not in', ('receivable', 'payable'))]")
    default_account_id = fields.Many2one(
        'account.account', check_company=True, copy=False, ondelete='restrict',
        string='Default Account',
        domain="[('deprecated', '=', False), ('company_id', '=', company_id),"
               "('user_type_id.type', 'not in', ('receivable', 'payable'))]")
    suspense_account_id = fields.Many2one(
        'account.account', check_company=True, ondelete='restrict', readonly=False, store=True,
        compute='_compute_suspense_account_id',
        help="Bank statements transactions will be posted on the suspense account until the final reconciliation "
             "allowing finding the right account.", string='Suspense Account',
        domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id), \
                                 ('user_type_id.type', 'not in', ('receivable', 'payable'))]")

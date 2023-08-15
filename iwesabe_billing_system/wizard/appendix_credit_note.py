# See LICENSE file for full copyright and licensing details

from odoo import models, fields, api


class AppendixCreditNote(models.TransientModel):
    _name = 'appendix.credit.note'
    _description = 'Appendix Credit Note'

    @api.depends('invoice_line_ids')
    def get_payment_amount(self):
        for res in self:
            res.credit_note_amount = 0.0
            res.invoiced_amount = sum([inv.invoice_amount for inv in res.invoice_line_ids])
            res.paid_amount = sum([inv.invoice_amount - inv.unpaind_amount for inv in res.invoice_line_ids])
            res.unpaid_amount = sum([inv.unpaind_amount for inv in res.invoice_line_ids])
            if res.credit_note_for == 'airline':
                res.credit_note_amount = res.invoice_appendix_id.fees_total_total - res.unpaid_amount

    credit_note_for = fields.Selection([('airline', 'Airine Company'), ('non_airline', 'Non Airline')], string="Credit Note For", default="airline")
    invoice_appendix_id = fields.Many2one('invoice.appendix', string="Invoice")
    partner_id = fields.Many2one('res.partner', string="Partner")
    invoiced_amount = fields.Monetary(string="Invoiced Amount", compute="get_payment_amount")
    paid_amount = fields.Monetary(string="Paid Amount", compute="get_payment_amount")
    unpaid_amount = fields.Monetary(string="Unpaid Amount", compute="get_payment_amount")
    appendix_invoice_amount = fields.Float(related="invoice_appendix_id.fees_total_total", string="Appendix Invoice Amount")
    invoice_line_ids = fields.One2many('invoice.line.detail', 'credit_note_id', string="Invoices")

    credit_note_amount = fields.Monetary(string="Credit Note Amount", compute="get_payment_amount")
    currency_id = fields.Many2one('res.currency', string="Currency")
    account_id = fields.Many2one('account.account', string="account")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id, help='The company this user is currently working for.', context={'user_preference': True})

    @api.onchange('credit_note_for')
    def onchanhge_credit_note_for(self):
        self.partner_id = False
        if self.invoice_appendix_id:
            if self.credit_note_for == 'airline':
                self.partner_id = self.invoice_appendix_id.partner_id.id
                return {'domain': {'partner_id': [('id', '=', self.partner_id.id)]}}
            if self.credit_note_for == 'non_airline':
                invoice_ids = self.env['account.move'].search([('appendix_id', '=', self.invoice_appendix_id.id), ('appendix_another_customer', '=', True), ('move_type', '=', 'out_invoice'), ('state', '=', 'posted')])
                partner_ids = [inv.partner_id.id for inv in invoice_ids]
                return {'domain': {'partner_id': [('id', 'in', partner_ids)]}}

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.invoice_line_ids = False
        if self.partner_id and self.invoice_appendix_id:
            common_domain = [('appendix_id', '=', self.invoice_appendix_id.id), ('partner_id', '=', self.partner_id.id), ('move_type', '=', 'out_invoice'), ('state', '=', 'posted')]
            if self.credit_note_for == 'airline':
                invoices = self.env['account.move'].search(common_domain + [('appendix_another_customer', '=', False)])
            if self.credit_note_for == 'non_airline':
                invoices = self.env['account.move'].search(common_domain + [('appendix_another_customer', '=', True)])
            if invoices:
                inv_list = []
                for inv in invoices:
                    inv_list.append((0, 0, {'invoice_id': inv.id}))
                self.write({'invoice_line_ids': inv_list})

    def create_invoice_credit_note(self):
        if self.partner_id:
            pass
            invoice_lines = [(0, 0, {
                'name': "refund Invoice for %s" % self.invoice_appendix_id.name,
                'account_id': self.account_id.id,
                'price_unit': self.credit_note_amount or 0.0
            })]
            vals = {
                    'appendix_id': self.invoice_appendix_id.id,
                    'appendix_another_customer': False,
                    'move_type': 'out_refund',
                    'invoice_date': fields.Date.today(),
                    'date': fields.Date.today(),
                    'invoice_origin': self.invoice_appendix_id.name,
                    'customer_contact_id': self.partner_id.child_ids[0] if self.partner_id.child_ids else False,
                    'partner_id': self.partner_id.id,
                    'invoice_user_id': self.env.user.id,
                    'invoice_line_ids': invoice_lines,
                }
            # Invoice Creating
            self.env['account.move'].create(vals)
            self.invoice_appendix_id.action_open_related_invoices()


class AppedixCreditLine(models.TransientModel):
    _name = 'invoice.line.detail'
    _description = "Invoice lINE Detail"

    credit_note_id = fields.Many2one('appendix.credit.note', string="CN")
    invoice_id = fields.Many2one('account.move', string="Invoice#")
    invoice_amount = fields.Monetary(related="invoice_id.amount_total")
    paid_amount = fields.Monetary(string="Paid Amount")
    unpaind_amount = fields.Monetary(related="invoice_id.amount_residual")
    currency_id = fields.Many2one(related="invoice_id.currency_id", string="Currency")

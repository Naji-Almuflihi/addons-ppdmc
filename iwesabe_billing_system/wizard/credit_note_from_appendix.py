# See LICENSE file for full copyright and licensing details

from odoo import models, fields


class CrediteNoteFromAppendix(models.TransientModel):
    _name = 'invoice.credit.note'

    appendix_id = fields.Many2one('revenue.appendix', string="Revenue Appendix")
    applendix_line_id = fields.Many2one("revenue.appendix.line", string="Revenue Appendix Line")
    old_invoice_id = fields.Many2one('account.move', string="Old Invoice")
    old_invoice_amount = fields.Monetary(related="old_invoice_id.amount_total", string="Old Invoice Amount")
    new_invoice_id = fields.Many2one('account.move', string="New Invoice")
    new_invoice_amount = fields.Monetary(related="new_invoice_id.amount_total", string="New Invoice Amount")
    currency_id = fields.Many2one('res.currency', store=True, readonly=True, string='Currency')
    diff_amount = fields.Float(string="Diff Amount")
    account_id = fields.Many2one('account.account', string="Account")

    def create_credit_note(self):
        account_inv_obj = self.env['account.move']
        invoice_lines = [(0, 0, {
                    'name': "Diff Amount for %s and %s" % (self.old_invoice_id.name, self.new_invoice_id.name),
                    # 'product_id': term_facilities_utilization.id,
                    'account_id': self.account_id.id,
                    'price_unit': abs(self.diff_amount)
                })]
        vals = {
                'appendix_id': self.applendix_line_id.invoice_id.id,
                'revenue_id': self.appendix_id.id,
                'move_type': 'out_refund',
                'invoice_date': fields.Date.today(),
                'invoice_date_due': fields.Date.today(),
                'date': fields.Date.today(),
                'invoice_origin': self.applendix_line_id.invoice_id.name,
                'customer_contact_id': self.applendix_line_id.partner_id.child_ids[0] if self.applendix_line_id.partner_id.child_ids else False,
                'partner_id': self.applendix_line_id.partner_id.id,
                'invoice_user_id': self.env.user.id,
                'invoice_line_ids': invoice_lines}
        invoice_id = account_inv_obj.create(vals)
        print ("invoice id", invoice_id)

    def create_invoice(self):
        print ("create_invoice")
        account_inv_obj = self.env['account.move']
        invoice_lines = [(0, 0, {
                    'name': "Diff Amount for %s and %s" % (self.old_invoice_id.name, self.new_invoice_id.name),
                    # 'product_id': term_facilities_utilization.id,
                    'account_id': self.account_id.id,
                    'price_unit': abs(self.diff_amount)
                })]
        vals = {
                'appendix_id': self.applendix_line_id.invoice_id.id,
                'move_type': 'out_invoice',
                'revenue_id': self.appendix_id.id,
                'invoice_date': fields.Date.today(),
                'invoice_date_due': fields.Date.today(),
                'date': fields.Date.today(),
                'invoice_origin': self.applendix_line_id.invoice_id.name,
                'customer_contact_id': self.applendix_line_id.partner_id.child_ids[0] if self.applendix_line_id.partner_id.child_ids else False,
                'partner_id': self.applendix_line_id.partner_id.id,
                'invoice_user_id': self.env.user.id,
                'invoice_line_ids': invoice_lines}
        invoice_id = account_inv_obj.create(vals)
        print ("invoice id", invoice_id)

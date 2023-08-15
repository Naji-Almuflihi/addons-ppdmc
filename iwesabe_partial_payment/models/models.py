from odoo import models, fields, api


class MultiMoveLineInherit(models.Model):
    _inherit = 'multi.move.line'

    invoice_date = fields.Date(string="Invoice Date", related='move_id.invoice_date')
    supplier_site_id = fields.Many2one("site.solution", string="Supplier Site Solution", compute='compute_supplier_site')
    ref = fields.Char(string="Reference", related='move_id.ref')
    move_type = fields.Selection(selection=[('out_invoice', 'Out Invoice'), ('in_invoice', 'In Invoice')], related='multi_payment_id.move_type')

    @api.depends('move_id')
    def compute_supplier_site(self):
        for rec in self:
            if rec.move_id.supplier_site_id:
                rec.supplier_site_id = rec.move_id.supplier_site_id.id
            else:
                rec.supplier_site_id = False


class AccountMultiPaymentWizardInherit(models.Model):
    _inherit = 'account.multi.payment.wizard'

    move_type = fields.Selection([('out_invoice', 'Out Invoice'), ('in_invoice', 'In Invoice'), ], required=False, )

    @api.onchange('partner_id', 'payment_type')
    def filter_payment_line(self):
        account_move_line_record = self.env['account.move.line'].search([])
        account_move_line_list = []
        if self.env.context.get('active_model') == 'account.payment':
            payment_record = self.env['account.payment'].browse(self._context.get('active_ids'))
            lines_list = []
            counter = 0
            if payment_record:
                account_move_record = self.env['account.move'].search([('id', '=', payment_record.move_id.id)], limit=1)
                if account_move_record:
                    for line in account_move_record.line_ids:
                        counter += 1
                        lines_list.append(line.id)
            if counter > 1:
                return {'domain': {'move_line_id': [('id', 'in', lines_list)]}}
            else:
                self.move_line_id = lines_list[0]

        else:
            if self.partner_type == 'customer':
                self.move_type = 'out_invoice'
                for line in account_move_line_record:
                    bank_cash_id = self.env.ref('account.data_account_type_liquidity').id
                    credit_card_id = self.env.ref('account.data_account_type_credit_card').id

                    if line.debit > 0 and line.partner_id.id == self.partner_id.id and line.move_id.state == 'posted' and line.account_id.user_type_id.id in [bank_cash_id, credit_card_id]:
                        account_move_line_list.append(line.id)
                return {'domain': {'move_line_id': [('id', 'in', account_move_line_list)]}}

            elif self.partner_type == 'supplier':
                self.move_type = 'in_invoice'
                for line in account_move_line_record:

                    bank_cash_id = self.env.ref('account.data_account_type_liquidity').id
                    credit_card_id = self.env.ref('account.data_account_type_credit_card').id

                    if line.credit > 0 and line.partner_id.id == self.partner_id.id and line.move_id.state == 'posted' and line.account_id.user_type_id.id in [bank_cash_id, credit_card_id]:
                        account_move_line_list.append(line.id)
                return {'domain': {'move_line_id': [('id', 'in', account_move_line_list)]}}

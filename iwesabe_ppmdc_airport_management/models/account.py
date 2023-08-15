# See LICENSE file for full copyright and licensing details

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"
    _description = "Account Entry"

    property_id = fields.Many2one('property.property', help='Asset')
    schedule_date = fields.Date(string='Schedule Date', help='Rent Schedule Date.')
    source = fields.Char(string='Account Source', help='Source from where account move created.')

    tenancy_phone_id = fields.Many2one('tenancy.phone.extention', string='Tenancy Phone')
    tenancy_service_id = fields.Many2one('tenancy.service', string='Tenancy Service')
    service_contract_id = fields.Many2one('tenancy.service.contract', string='Service Contract')
    tenancy_id = fields.Many2one('tenant.tenancy', string='tenancy')
    phone_extention_ids = fields.One2many('phone.extention.service.invoice', 'move_id', string="Phone Extenions Number")
    # phone_extention_id = fields.Many2one("phone.extention.invoice", string="Phone Extention")

    def assert_balanced(self):
        prec = self.env['decimal.precision'].precision_get('Account')
        if self.ids:
            self._cr.execute("""
                SELECT move_id FROM account_move_line WHERE move_id in %s
                GROUP BY move_id HAVING abs(sum(debit) - sum(credit)) > %s
                """, (tuple(self.ids), 10 ** (-max(5, prec))))
            if self._cr.fetchall():
                raise UserError(_("Cannot create unbalanced journal entry."))
        return True

    property_id = fields.Many2one('property.property', string='Property', help='Property Name.')
    new_tenancy_id = fields.Many2one('tenant.tenancy', string='Tenancy.')

    def action_move_create(self):
        res = super(AccountMove, self).action_move_create()
        for inv_rec in self:
            if inv_rec.move_id and inv_rec.move_id.id:
                inv_rec.move_id.write({
                    'property_id': inv_rec.property_id.id or False,
                    'ref': 'Maintenance Invoice',
                    'source': inv_rec.property_id.name or False})
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    property_id = fields.Many2one('property.property', string='Property', help='Property Name.')


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    tenancy_id = fields.Many2one('tenant.tenancy', string='Tenancy', help='Tenancy Name.')
    property_id = fields.Many2one('property.property', string='Property', help='Property Name.')
    amount_due = fields.Monetary(related='partner_id.credit', readonly=True, default=0.0, help='Display Due amount of Customer')
    non_receivable_payable = fields.Boolean(string="Non receivables and payables", tracking=True, default=False)
    custom_dest_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Destination Account',
        domain="[('company_id', '=', company_id)]")

    def onchange_custom_dest_account_id(self):
        if self.custom_dest_account_id:
            self.destination_account_id = self.custom_dest_account_id.id

    def post(self):
        res = super(AccountPayment, self).post()
        invoice_obj = self.env['account.move']
        context = dict(self._context or {})
        for rec in self:
            if context.get('return'):
                invoice_browse = invoice_obj.browse(
                    context.get('active_id')).new_tenancy_id
                invoice_browse.write({'amount_return': rec.amount})
            if context.get('deposite_received'):
                tenancy_active_id = self.env['tenant.tenancy'].browse(context.get('active_id'))
                tenancy_active_id.write({'amount_return': rec.amount})
        return res

    @api.model
    def create(self, vals):
        res = super(AccountPayment, self).create(vals)
        if res and res.id and res.tenancy_id and res.tenancy_id.id:
            if res.payment_type == 'inbound':
                res.tenancy_id.write({'acc_pay_dep_rec_id': res.id})
            if res.payment_type == 'outbound':
                res.tenancy_id.write({'acc_pay_dep_ret_id': res.id})
        return res

    def back_to_tenancy(self):
        """
        This method will open a Tenancy form view.
        @param self: The object pointer
        @param context: A standard dictionary for contextual values
        """
        self.ensure_one()
        open_move_id = self.env.ref('iwesabe_ppmdc_airport_management.view_tenant_tenancy_form').id
        return {
                'view_type': 'form',
                'view_id': open_move_id,
                'view_mode': 'form',
                'res_model': 'tenant.tenancy',
                'res_id': self.tenancy_id and self.tenancy_id.id,
                'type': 'ir.actions.act_window',
                'target': 'current',
                'context': self._context,
            }

    # Gives Credit amount line
    def _get_counterpart_move_line_vals(self, invoice=False):
        rec = super(AccountPayment, self)._get_counterpart_move_line_vals(
            invoice=invoice)
        if rec and self.tenancy_id and self.tenancy_id.id:
            if self.payment_type in ('inbound', 'outbound'):
                rec.update({'analytic_account_id': False})
        return rec

    # Gives Debit amount line
    def _get_liquidity_move_line_vals(self, amount):
        rec = super(
            AccountPayment, self)._get_liquidity_move_line_vals(amount)
        if rec and self.tenancy_id and self.tenancy_id.id:
            if self.payment_type in ('inbound', 'outbound'):
                rec.update({'analytic_account_id': self.tenancy_id.id})
        return rec

    def _create_payment_entry(self, amount):
        move = super(AccountPayment, self)._create_payment_entry(amount)
        if move and move.id and self.property_id and self.property_id.id:
            move.write({'property_id': self.property_id.id or False,
                        'source': self.tenancy_id.name or False})
        return move

    @api.depends('journal_id', 'partner_id', 'partner_type', 'is_internal_transfer', 'custom_dest_account_id')
    def _compute_destination_account_id(self):
        self.destination_account_id = False
        for pay in self:
            if pay.custom_dest_account_id:
                pay.destination_account_id = pay.custom_dest_account_id.id
            elif pay.is_internal_transfer:
                pay.destination_account_id = pay.journal_id.company_id.transfer_account_id
            elif pay.partner_type == 'customer':
                # Receive money from invoice or send money to refund it.
                if pay.partner_id:
                    pay.destination_account_id = pay.partner_id.with_company(
                        pay.company_id).property_account_receivable_id
                else:
                    pay.destination_account_id = self.env['account.account'].search([
                        ('company_id', '=', pay.company_id.id),
                        ('internal_type', '=', 'receivable'),
                        ('deprecated', '=', False),
                    ], limit=1)
            elif pay.partner_type == 'supplier':
                # Send money to pay a bill or receive money to refund it.
                if pay.partner_id:
                    pay.destination_account_id = pay.partner_id.with_company(pay.company_id).property_account_payable_id
                else:
                    pay.destination_account_id = self.env['account.account'].search([
                        ('company_id', '=', pay.company_id.id),
                        ('internal_type', '=', 'payable'),
                        ('deprecated', '=', False),
                    ], limit=1)


class PhoneExtentionServiceInvoice(models.Model):
    _name = 'phone.extention.service.invoice'
    _description = "Phone Extention Service"

    move_id = fields.Many2one('account.move', string="Invoice")
    phone_extention_id = fields.Many2one('phone.extention', string="Phone Extention Service")
    extention_number_id = fields.Many2one('phone.extentaion.numbers', string="Extention Number")
    location_id = fields.Many2one("property.property", string="Location")

    @api.onchange('phone_extention_id')
    def onchange_phone_extention_id(self):
        if self.phone_extention_id:
            self.extention_number_id = False

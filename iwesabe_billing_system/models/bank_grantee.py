from odoo import models, fields, api


class BankGrantee(models.Model):
    _name = 'bank.grantee'
    _inherit = ['mail.thread']
    _rec_name = 'name'

    name = fields.Char(string="Name", default='New')
    partner_id = fields.Many2one("res.partner", string="Customer", track_visibility='always')
    bank_id = fields.Many2one("res.bank", string="Bank Grantee", track_visibility='always', )
    start_date = fields.Date(string="Start Date", track_visibility='always')
    end_date = fields.Date(string="End Date", track_visibility='always')
    amount = fields.Float(string="Grantee Amount", track_visibility='always')
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('under_renew', 'Under renew process'),
                              ('liquefaction', 'Liquefaction'), ('closed', 'Closed')], default='draft', track_visibility='always', string="Status")
    airline_service_contract_id = fields.Many2one("airline.service.contract", string="")
    payment_bank_grantee_count = fields.Integer(string="", compute='get_payment_count')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    bank_grantee_ref = fields.Char(string="Bank Grantee Ref")

    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('bank.grantee.seq')
        vals.update({'name': name})
        res = super(BankGrantee, self).create(vals)
        return res

    @api.model
    def get_email_to(self):
        email_list = []
        account_user_group = self.env.ref("account.group_account_user")
        email_list += [usr.partner_id.email for usr in account_user_group.users if usr.partner_id.email]
        return email_list

    def confirm_button(self):
        self.state = 'confirmed'
        self.action_send_mail()

    def action_send_mail(self):
        template = self.env.ref('iwesabe_billing_system.email_send_for_bank_gauantee')
        assert template._name == 'mail.template'
        email_to_list = self.get_email_to()
        for user in email_to_list:
            template_values = {'email_to': user}
            template.sudo().write(template_values)
            template.sudo().send_mail(self.id, force_send=True, raise_exception=True)

    def renew_button(self):
        self.state = 'under_renew'

    def liquefaction_button(self):
        self.state = 'liquefaction'

    def create_payment(self):
        ctx = {
            'default_partner_id': self.partner_id.id,
            'default_payment_type': 'inbound',
            'default_partner_type': 'customer',
            'default_amount': self.amount,
            'default_bank_grantee_id': self.id,
            'default_check_bank_grantee': True,
            'default_is_bank_grantee': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.payment',
            'target': 'current',
            'context': ctx,
        }

    @api.depends()
    def get_payment_count(self):
        self.payment_bank_grantee_count = self.env['account.payment'].search_count([('bank_grantee_id', '=', self.id)])

    def open_payment_bank_grantee(self):
        return {
            'name': 'Customer Payment',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'domain': [('bank_grantee_id', '=', self.id)],
            'target': 'current',
        }

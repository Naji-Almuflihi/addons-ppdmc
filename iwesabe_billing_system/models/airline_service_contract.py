from odoo import models, fields, api


class AirlineServiceContract(models.Model):
    _name = 'airline.service.contract'
    _inherit = ['mail.thread']

    ARRAY_READONLY = {
        'open': [('readonly', True)],
        'cancelled': [('readonly', True)],
    }

    name = fields.Char(string="Name", default="New")
    date = fields.Date(string="Date", default=fields.Date.context_today, track_visibility='always')
    partner_id = fields.Many2one("res.partner", string="Customer", track_visibility='always')
    amount = fields.Float(string="Amount")
    contact_id = fields.Many2one("res.partner", string="Contact", track_visibility='always')
    start_date = fields.Date(string="Start Date", track_visibility='always')
    end_date = fields.Date(string="End Date", track_visibility='always')
    contract_type = fields.Selection([('bank_grantee', 'Bank Grantee'), ('advance_payments', 'Advance payments'), ('agent_grantee', 'Agent Grantee'), ('without_agent_monthly_invoices', 'without grantee Monthly Invoices')],
                                     string="Payment Grantee options", track_visibility='always')
    services_ids = fields.Many2many("product.product", string="Services", track_visibility='always')
    bank_grantee_count = fields.Integer(string="", compute='get_bank_grantee_count')
    agent_grantee_count = fields.Integer(string="", compute='get_agent_grantee_count')
    payment_count = fields.Integer(string="", compute='get_payment_count')
    flight_type = fields.Selection([('charter_flight', 'Charter Flight'), ('normal', 'Normal'), ('', '')], string="")
    gsa_text = fields.Char(string="GSA")

    expected_flight_from = fields.Date(string="Expected Flight From")
    expected_flight_To = fields.Date(string="Expected Flight To")
    summary = fields.Html(states=ARRAY_READONLY)
    auto_renewal = fields.Selection(string="Auto Renewal", selection=[('yes', 'Yes'), ('no', 'No')])
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], string="Status", default='draft', track_visibility='onchange')

    @api.onchange('contract_type')
    def onchange_contract_type(self):
        self.summary = ''
        if self.contract_type:
            doc_id = self.env['contract.type.document'].search([('contract_type', '=', self.contract_type)], limit=1)
            if doc_id:
                self.summary = doc_id.description

    def button_set_to_draft(self):
        self.write({'state': 'draft'})

    def button_cancel(self):
        self.write({'state': 'cancelled'})

    def button_confirm(self):
        self.write({'state': 'confirm'})

    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('airline.service.contract.seq')
        vals.update({'name': name})
        res = super(AirlineServiceContract, self).create(vals)
        return res

    @api.onchange('date', 'partner_id')
    def get_contacts(self):
        return {'domain': {'contact_id': [('id', 'in', self.partner_id.child_ids.ids)]}}

    def bank_grantee_button(self):
        ctx = {
            'default_partner_id': self.partner_id.id,
            'default_amount': self.amount,
            'default_airline_service_contract_id': self.id,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'bank.grantee',
            'target': 'current',
            'context': ctx,
        }

    @api.depends()
    def get_bank_grantee_count(self):
        self.bank_grantee_count = self.env['bank.grantee'].search_count([('airline_service_contract_id', '=', self.id)])

    def open_bank_grantee(self):
        return {
            'name': 'Bank Grantee',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'bank.grantee',
            'domain': [('airline_service_contract_id', '=', self.id)],
            'target': 'current',
        }

    def agent_grantee_button(self):
        ctx = {
            'default_partner_id': self.partner_id.id,
            'default_start_date': self.start_date,
            'default_end_date': self.end_date,
            'default_amount': self.amount,
            'default_agent_grantee_id': self.partner_id.agent_grantee_id.id,
            'default_name': str('Agent Grantee For ') + str(self.partner_id.name) + str(' With Amount ') + str(self.amount),
            'default_airline_service_contract_id': self.id,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'agent.grantee',
            'target': 'current',
            'context': ctx,
        }

    @api.depends()
    def get_agent_grantee_count(self):
        self.agent_grantee_count = self.env['agent.grantee'].search_count([('airline_service_contract_id', '=', self.id)])

    def open_agent_grantee(self):
        return {
            'name': 'Agent Grantee',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'agent.grantee',
            'domain': [('airline_service_contract_id', '=', self.id)],
            'target': 'current',
        }

    def account_move_button(self):
        sales_congig_setting_rec = self.env['res.config.settings'].search([], limit=1)
        lines = [(5, 0, 0)]
        if sales_congig_setting_rec.deposit_default_product_id:
            lines.append((0, 0, {
                'product_id': sales_congig_setting_rec.deposit_default_product_id.id,
                'name': sales_congig_setting_rec.deposit_default_product_id.name,
                'price_unit': self.amount
            }))
        values = {
            'partner_id': self.partner_id.id,
            'move_type': 'out_invoice',
            'invoice_date': self.start_date,
            'invoice_line_ids': lines,
            'airline_services_contract_id': self.id,
            'is_services_contract': True,
        }

        invoice_record = self.env['account.move'].create(values)
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': invoice_record.id,
            'target': 'current',
        }

    @api.depends()
    def get_payment_count(self):
        self.payment_count = self.env['account.payment'].search_count([('airline_service_contract_id', '=', self.id)])

    def open_payment(self):
        return {
            'name': 'Payments',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'domain': [('airline_service_contract_id', '=', self.id)],
            'target': 'current',
        }

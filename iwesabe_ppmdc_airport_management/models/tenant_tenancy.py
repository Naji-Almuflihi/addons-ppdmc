# See LICENSE file for full copyright and licensing details

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import time

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, Warning, UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class TenantTenancy(models.Model):
    _name = "tenant.tenancy"
    _inherit = ["account.analytic.account", 'mail.thread',
                'mail.activity.mixin', 'portal.mixin']
    _order = 'code'

    ARRAY_READONLY = {
        'open': [('readonly', True)],
        'pending': [('readonly', True)],
        'close': [('readonly', True)],
        'cancelled': [('readonly', True)],

    }
    ARRAY_READONLY_CD = {
        'close': [('readonly', True)],
        'cancelled': [('readonly', True)],
    }

    @api.depends('account_move_line_ids')
    def _compute_total_deb_cre_amt(self):
        """
        This method is used to calculate Total income amount.
        @param self: The object pointer
        """
        for tenancy_brw in self:
            total = tenancy_brw.total_credit_amt - tenancy_brw.total_debit_amt
            tenancy_brw.total_deb_cre_amt = total or 0.0

    @api.depends('account_move_line_ids')
    def _compute_total_credit_amt(self):
        """
        This method is used to calculate Total credit amount.
        @param self: The object pointer
        """
        for tenancy_brw in self:
            tenancy_brw.total_credit_amt = sum(
                credit_amt.credit for credit_amt in
                tenancy_brw.account_move_line_ids)

    @api.depends('account_move_line_ids')
    def _compute_total_debit_amt(self):
        """
        This method is used to calculate Total debit amount.
        @param self: The object pointer
        """
        for tenancy_brw in self:
            tenancy_brw.total_debit_amt = sum(
                debit_amt.debit for debit_amt in
                tenancy_brw.account_move_line_ids)

    name = fields.Char(track_visibility='onchange', required=False)
    name_seq = fields.Char()
    name_seq_start = fields.Char(default="خ م ")

    contract_attachment = fields.Binary(string='Tenancy Contract', help='Contract document attachment for selected property', states=ARRAY_READONLY)
    is_property = fields.Boolean(string='Is Property?')
    rent_entry_chck = fields.Boolean(string='Rent Entries Check', default=False)
    code = fields.Char(string='Reference', track_visibility='onchange')
    doc_name = fields.Char(string='Filename', track_visibility='onchange')
    date_end = fields.Date(string='Expiration Date', index=True, help="Tenancy contract end date.", track_visibility='onchange')
    date_end_hijri = fields.Char(string="Expiration Date Hijri", track_visibility='onchange')
    date_start = fields.Date(string='Start Date', default=lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT), help="Tenancy contract start date .", track_visibility='onchange')
    date_start_hijri = fields.Char(string="Start Date Hijri", track_visibility='onchange')
    date_order = fields.Date(string='Date', default=lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT), index=True, help="Tenancy contract creation date.", track_visibility='onchange', states=ARRAY_READONLY)
    date_order_hijri = fields.Char(string="Hijei Date", states=ARRAY_READONLY)
    amount_fee_paid = fields.Integer(string='Amount of Fee Paid', track_visibility='onchange')
    tenant_id = fields.Many2one('res.partner', string='Tenant', help="Tenant Name of Tenancy.", track_visibility='onchange')
    contact_id = fields.Many2one('res.partner', string='Contact', help="Contact person name.", track_visibility='onchange', states=ARRAY_READONLY)
    rent_schedule_ids = fields.One2many('tenancy.rent.schedule', 'tenancy_id', string='Rent Schedule', states=ARRAY_READONLY_CD)
    account_move_line_ids = fields.One2many('account.move.line', 'analytic_account_id', string='Entries', readonly=True, states={'draft': [('readonly', False)]})
    total_rent = fields.Monetary(string='Total Rent', store=True, readonly=True, currency_field='currency_id', compute='compute_total_amount', help='Total rent of this Tenancy.')
    total_debit_amt = fields.Monetary(string='Total Debit Amount', default=0.0, compute='_compute_total_debit_amt', currency_field='currency_id')
    total_credit_amt = fields.Monetary(string='Total Credit Amount', default=0.0, compute='_compute_total_credit_amt', currency_field='currency_id')
    total_deb_cre_amt = fields.Monetary(string='Total Expenditure', default=0.0, compute='_compute_total_deb_cre_amt', currency_field='currency_id')
    description = fields.Text(string='Description', help='Additional Terms and Conditions')
    duration_cover = fields.Text(string='Duration of Cover', help='Additional Notes')
    acc_pay_dep_rec_id = fields.Many2one('account.payment', string='Account Payment', copy=False, help="Manager of Tenancy.")
    acc_pay_dep_ret_id = fields.Many2one('account.payment', string='Tenancy Manager', copy=False, help="Manager of Tenancy.")
    rent_type_id = fields.Many2one('rent.type', string='Season Rent', states=ARRAY_READONLY)
    deposit_scheme_type = fields.Selection([('insurance', 'Insurance-based')], 'Type of Scheme')
    stage = fields.Selection([('new', 'New'), ('running', 'Running'), ('Renewal', 'Renewal'), ('cancel', 'Cancel')], string="Stage", default="new")
    state = fields.Selection(
        [('template', 'Template'),
         ('draft', 'New'),
         ('open', 'In Progress'),
         ('pending', 'To Renew'),
         ('close', 'Closed'),
         ('cancel_requisition', 'Cancel Requisition'),
         ('cancelled', 'Cancelled')],
        string='Status', required=True, copy=False, default='draft', track_visibility='onchange')
    invoice_ids = fields.One2many('account.move', 'tenancy_id', string="Tenancy")
    multi_prop = fields.Boolean(string='Multiple Property', help="Check this box Multiple property.")
    penalty_a = fields.Boolean('Penalty')
    recurring = fields.Boolean('Recurring')
    main_cost = fields.Float(string='Maintenance Cost', default=0.0, help="Insert maintenance cost")
    tenancy_cancelled = fields.Boolean(string='Tanency Cancelled', default=False)
    annual_rate = fields.Float(string="Annual increase rate(%)", default="10", states=ARRAY_READONLY)
    insurance_rate = fields.Float(string="Insurance rate(%)", default="10")
    property_ids = fields.One2many('tenancy.property', 'tenancy_id', string="Property", states=ARRAY_READONLY_CD)
    service_contract_ids = fields.One2many('tenancy.service.contract', 'tenancy_id', string="Service Contract", states=ARRAY_READONLY_CD)
    service_contract_count = fields.Integer(string="Service Count", compute='_compute_service_contract_count', store=True)
    invoice_count = fields.Integer(string="Invoice count", compute='_compute_invoice_count', store=True)
    service_application_id = fields.Many2one('service.application', string='Service Application')
    information_data_ids = fields.One2many('tenancy.service', 'tenancy_id', string="Information Data")
    telephone_service_ids = fields.One2many('service.contract.phone.extention', 'tenancy_id', string="Telephone Servcie")
    equipment_ids = fields.One2many('tenancy.equipment', 'tenancy_id', string="Equipments")
    amount_residual = fields.Float(string="Invoice Amount Due", compute='compute_amount_residual')
    amount_total = fields.Float(string="Invoice Total Amount", compute='compute_amount_residual')
    paid_amount = fields.Float(string="Invoice Paid Amount", compute='compute_amount_residual')
    hijri_date = fields.Char()

    is_cancel_tenancy_user = fields.Boolean(compute='check_cancel_tenancy_user')
    import_number = fields.Char("Import Number")

    amount_untaxed = fields.Float(string="Untaxed Amount :", compute='compute_total_amount')
    amount_tax = fields.Float(string="Tax :", compute='compute_total_amount')
    amount_taxed_total = fields.Float(string="Total :", compute='compute_total_amount')
    insurance_value = fields.Float(string="Insurance Value", compute='compute_insurance_value')
    customer_balance = fields.Float(string="Customer Balance", compute='compute_customer_balance')
    payment_count = fields.Integer(string="Invoice count", compute='_compute_invoice_payment', store=True)
    payment_ids = fields.One2many('account.payment', 'tenancy_id', string="Tenancy")

    @api.depends('tenant_id')
    def compute_customer_balance(self):
        for rec in self:
            if rec.tenant_id:
                rec.customer_balance = rec.tenant_id.credit - rec.tenant_id.debit
            else:
                rec.customer_balance = 0

    @api.depends('insurance_rate', 'total_rent')
    def compute_insurance_value(self):
        for rec in self:
            rec.insurance_value = rec.insurance_rate*rec.total_rent/100

    @api.depends('property_ids')
    def compute_total_amount(self):
        for rec in self:
            rec.amount_untaxed = 0.0
            rec.amount_tax = 0.0
            rec.amount_total = 0.0
            amount_untaxed = 0.0
            total_tax = 0.0

            if rec.property_ids:
                for line in rec.property_ids:
                    amount_untaxed += line.total
                    tax_amount = 0.0
                    for tax in line.vat_ids:
                        tax_amount += (tax.amount * line.total) / 100
                    total_tax += tax_amount

            rec.amount_untaxed = amount_untaxed
            rec.amount_tax = total_tax
            rec.amount_taxed_total = rec.amount_untaxed + rec.amount_tax
            rec.total_rent = rec.amount_taxed_total

    @api.depends('state')
    def check_cancel_tenancy_user(self):
        for rec in self:
            if rec.env.user.id == rec.env.company.cancellation_tenancy_approval_id.id:
                rec.is_cancel_tenancy_user = True
            else:
                rec.is_cancel_tenancy_user = False
    # @api.depends('date_start_hijri')
    # def compute_hijri_date(self):
    #     for rec in self:
    #         if rec.date_start_hijri:
    #             hijri_date = self.date_start_hijri.rsplit('/')
    #             rec.hijri_date= hijri_date[2][2:]
    #         else:
    #             rec.hijri_date=""

    @api.depends('invoice_count')
    def compute_amount_residual(self):
        for rec in self:
            amount_residual = 0.0
            amount_total = 0.0
            for inv in self.env['account.move'].search([('tenancy_id', '=', rec.id)]):
                amount_residual += inv.amount_residual
                amount_total += inv.amount_total
            rec.amount_residual = amount_residual
            rec.amount_total = amount_total
            rec.paid_amount = amount_total-amount_residual

    def name_get(self):
        res = []
        for record in self:
            name = str(record.name)
            res.append((record.id, name))
        return res

    def _prepare_information_data_ids(self):
        data = []
        if self.service_application_id:
            for rec in self.service_application_id.information_data_ids:
                data.append((0, 0, {
                    'product_id': rec.product_id.id,
                    'points': rec.points,
                    'vlan': rec.vlan,
                    'quantity': rec.quantity,
                    'rent': rec.rent,
                    'total': rec.total
                }))
            self.information_data_ids = data

    def _prepare_equipment_ids(self):
        data = []
        if self.service_application_id:
            for rec in self.service_application_id.equipment_ids:
                data.append((0, 0, {
                    'equipment_id': rec.equipment_id.id,
                    'quantity': rec.quantity,
                    'rent': rec.rent,
                    'total': rec.total
                }))
            self.equipment_ids = data

    def _prepare_telephone_service_ids(self):
        data = []
        if self.service_application_id:
            for rec in self.service_application_id.telephone_service_ids:
                data.append((0, 0, {
                    'equipment_id': rec.equipment_id.id,
                    'phone_extention_id': rec.phone_extention_id.id,
                    'extention_number_id': rec.extention_number_id.id,
                    'service_contract_id': rec.service_contract_id.id,
                    'quantity': rec.quantity,
                    'rent': rec.rent,
                    'total': rec.total
                }))
            self.telephone_service_ids = data

    def _prepare_property_ids(self):
        data = []
        if self.service_application_id:
            for rec in self.service_application_id.property_ids:
                data.append((0, 0, {
                    'property_id': rec.property_id.id,
                    'rent_type_id': rec.rent_type_id.id,
                    'season_year_id': rec.season_year_id.id,
                    'date_start': rec.date_start,
                    'date_end': rec.date_end,
                    'gfa_meter': rec.gfa_meter,
                    'rent': rec.rent,
                    'total': rec.total
                }))
            self.property_ids = data

    @api.onchange('service_application_id')
    def onchange_service_application_id(self):
        if self.service_application_id:
            self._prepare_information_data_ids()
            self._prepare_telephone_service_ids()
            self._prepare_equipment_ids()
            self._prepare_property_ids()
            self.date_order = self.service_application_id.date_order
            self.date_order_hijri = self.service_application_id.date_order_hijri
            self.date_start = self.service_application_id.date_start
            self.date_start_hijri = self.service_application_id.date_start_hijri
            self.date_end = self.service_application_id.date_end
            self.date_end_hijri = self.service_application_id.date_end_hijri
            self.annual_rate = self.service_application_id.annual_rate
            self.rent_type_id = self.service_application_id.rent_type_id.id
            self.total_rent = self.service_application_id.total_rent

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for record in self:
            record.invoice_count = len(record.invoice_ids.ids)

    @api.depends('payment_ids')
    def _compute_invoice_payment(self):
        for record in self:
            record.payment_count = len(record.payment_ids.ids)

    @api.onchange('date_order')
    def onchange_date_order(self):
        if self.date_order:
            self.with_context({'field_to': 'date_order_hijri', 'field_from': 'date_order'}).Gregorian2hijri()

    @api.onchange('date_start')
    def onchange_date_start(self):
        if self.date_start:
            self.with_context({'field_to': 'date_start_hijri', 'field_from': 'date_start'}).Gregorian2hijri()

    @api.onchange('date_end')
    def onchange_date_end(self):
        if self.date_end:
            self.with_context({'field_to': 'date_end_hijri', 'field_from': 'date_end'}).Gregorian2hijri()

    # @api.depends('property_ids.total')
    # def _compute_total_rent(self):
    #     """
    #     This method is used to calculate Total Rent of current Tenancy.
    #     @param self: The object pointer
    #     @return: Calculated Total Rent.
    #     """
    #     for rec in self:
    #         rec.total_rent = sum(r.total for r in self.property_ids)

    @api.depends('service_contract_ids')
    def _compute_service_contract_count(self):
        for record in self:
            record.service_contract_count = len(record.service_contract_ids.ids)

    @api.depends('phone_extention_ids')
    def _compute_phone_extention_count(self):
        for record in self:
            record.phone_extention_count = len(record.phone_extention_ids.ids)

    def action_view_phone_extention(self):
        actions = self.env.ref('iwesabe_ppmdc_airport_management.action_tenancy_phone').read()[0]
        actions['view_id'] = self.env.ref('iwesabe_ppmdc_airport_management.tenancy_other_service_form').id
        actions['domain'] = [('tenancy_id', '=', self.id)]
        actions['context'] = {'default_tenancy_id': self.id, 'default_partner_id': self.tenant_id.id}
        return actions

    def action_view_service(self):
        actions = self.env.ref('iwesabe_ppmdc_airport_management.actio_tenancy_service_contract').read()[0]
        actions['domain'] = [('tenancy_id', '=', self.id)]
        actions['context'] = {'default_tenancy_id': self.id, 'default_partner_id': self.tenant_id.id, 'create': 0}
        return actions

    def create_service_contract(self):
        # view = self.env.ref('iwesabe_ppmdc_airport_management.action_tenancy_service')
        view_id = self.env.ref('iwesabe_ppmdc_airport_management.tenancy_service_contract_form')
        return {
            'name': _('Service Contract'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'tenancy.service.contract',
            'views': [(view_id.id, 'form')],
            'view_id': view_id.id,
            'target': 'current',
            'context': {'default_tenancy_id': self.id, 'default_partner_id': self.tenant_id.id}
            }

    @api.constrains('date_start', 'date')
    def check_date_overlap(self):
        """
        This is a constraint method used to check the from date smaller than
        the Exiration date.
        @param self : object pointer
        """
        for rec in self:
            if rec.date_start and rec.date_end:
                if rec.date_end < rec.date_start:
                    raise ValidationError(_('Expiration date should be grater then Start Date!'))

    def unlink(self):
        """
        Overrides orm unlink method,
        @param self: The object pointer
        @return: True/False.
        """
        analytic_line_obj = self.env['account.analytic.line']
        rent_schedule_obj = self.env['tenancy.rent.schedule']
        for tenancy_rec in self:
            if tenancy_rec.state not in ('draft', 'cancelled'):
                state_description_values = {elem[0]: elem[1] for elem in self._fields['state']._description_selection(self.env)}
                raise UserError(_('You cannot delete a tenancy record which is in "%s" state.') % (state_description_values.get(tenancy_rec.state),))
            analytic_line_rec = analytic_line_obj.search([('account_id', '=', tenancy_rec.id)])
            if analytic_line_rec and analytic_line_rec.ids:
                analytic_line_rec.unlink()
            rent_ids = rent_schedule_obj.search([('tenancy_id', '=', tenancy_rec.id)])
            if any(rent.move_check for rent in rent_ids):
                raise Warning(_('You cannot delete Tenancy record, if any related Rent Schedule entries are in posted.'))
            else:
                rent_ids.unlink()
            if tenancy_rec.tenant_id and tenancy_rec.tenant_id.id:
                releted_user = tenancy_rec.tenant_id.id
                new_ids = self.env['res.users'].search([('partner_id', '=', releted_user)])
                if releted_user and new_ids and new_ids.ids:
                    new_ids.write({'tenant_ids': [(3, tenancy_rec.tenant_id.id)]})
        return super(TenantTenancy, self).unlink()

    @api.onchange('rent_type_id', 'date_start_hijri', 'name_seq_start')
    def compute_sequence_name_all(self):
        if self.name_seq:
            hijri_date = self.date_start_hijri.rsplit('/')
            self.hijri_date = hijri_date[2][2:]
            code = self.rent_type_id.code
            seq_code = str(code) + str(' / ') + str(self.name_seq_start) + str(' / ') + str(self.hijri_date)
            self.name = str(self.name_seq) + str(' / ') + str(seq_code)

    @api.model
    def create(self, vals):
        if vals['date_order_hijri']:
            code = self.env['rent.type'].browse(vals['rent_type_id']).code
            hijri_date = vals['date_start_hijri'].rsplit('/')
            vals['hijri_date'] = hijri_date[2][2:]
            seq_code = str(code) + str(' / ') + str(vals['name_seq_start']) + str(' / ') + str(vals['hijri_date'])
            seq = self.env['ir.sequence'].next_by_code('tenant.tenancy.sequence')
            vals.update({'name_seq': seq})
            vals['name'] = str(seq) + str(' / ') + str(seq_code)
        return super(TenantTenancy, self).create(vals)

    # def button_open_insurance_payment(self):
    #     return {
    #         'name': _('Journal Entry'),
    #         'res_model': 'account.move',
    #         'type': 'ir.actions.act_window',
    #         'view_id': False,
    #         'view_mode': 'form',
    #         'view_type': 'form',
    #         'target': 'new',
    #         'context': {'default_move_type': 'entry', 'default_ref': "Insurance Of  " + self.name}
    #     }

    def action_view_payment(self):
        print ("pass action_view_payment")
        payments = self.mapped('payment_ids')
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_account_payments")
        if len(payments) > 1:
            action['domain'] = [('id', 'in', payments.ids)]
        elif len(payments) == 1:
            form_view = [(self.env.ref('account.view_account_payment_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = payments.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_payment_type': 'inbound',
            'default_partner_type': 'customer',
            'default_partner_id': self.tenant_id.id,
            'default_tenancy_id': self.id,
            'create': 0,
        }
        action['context'] = context
        return action

    def button_open_insurance_payment(self):
        ''' Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        '''

        return {
            'name': _('Register Payment'),
            'res_model': 'account.payment',
            'view_mode': 'form',
            'context': {
                # 'active_model': 'account.move',
                # 'active_ids': self.ids,
                'default_tenancy_id': self.id,
                'default_amount': self.insurance_value,
                'default_payment_type': 'inbound',
                'default_partner_type': 'customer',
                'default_partner_id': self.tenant_id.id,
                'default_non_receivable_payable': True,
                'default_destination_account_id': self.tenant_id.property_account_receivable_id.id
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def button_start(self):
        """
        This button method is used to Change Tenancy state to Open.
        @param self: The object pointer
        """
        employee_mail_template = self.env.ref('iwesabe_ppmdc_airport_management.email_send_to_tenancy_started')

        user_obj = self.env['res.users']
        for current_rec in self:
            if current_rec.is_property:
                if current_rec.tenant_id and current_rec.tenant_id.id:
                    releted_user = current_rec.tenant_id.id
                    new_ids = user_obj.search([('partner_id', '=', releted_user)])
                    if releted_user and new_ids and new_ids.ids:
                        new_ids.write({'tenant_ids': [(4, current_rec.tenant_id.id)]})
            for user in self.env.ref('account.group_account_user').users:
                employee_mail_template.write({
                    'email_to': user.partner_id.email,
                    'email_from': current_rec.tenant_id.email,
                })
                employee_mail_template.send_mail(current_rec.id, force_send=True)
                thread_pool = self.sudo().env['mail.thread']
                thread_pool.message_notify(
                    partner_ids=[user.partner_id.id],
                    subject=str('Tenant Tenancy'),
                    body=str('This Tenant Tenancy ' + str(
                        current_rec.name) + ' In Progress') + ' click here to open: <a target=_BLANK href="/web?#id=' + str(
                        current_rec.id) + '&view_type=form&model=tenant.tenancy&action=" style="font-weight: bold">' + str(
                        current_rec.name) + '</a>',
                    email_from=self.env.user.company_id.catchall_formatted or self.env.user.company_id.email_formatted, )
        return self.write({'state': 'open', 'rent_entry_chck': False})

    def button_close(self):
        """
        This button method is used to Change Tenancy state to close.
        @param self: The object pointer
        """
        for rec in self:
            rec.write({'state': 'close'})

    def button_set_to_draft(self):
        """
        This button method is used to Change Tenancy state to close.
        @param self: The object pointer
        """
        for rec in self:
            rec.write({'state': 'draft', 'tenancy_cancelled': False})

    def button_reject_cancel_requests(self):
        self.state = 'cancel_requisition'

    def button_cancel_requests(self):
        self.state = 'cancel_requisition'

        employee_mail_template = self.env.ref('iwesabe_ppmdc_airport_management.email_send_to_tenancy_partner_cancel_requisition')
        employee_mail_template.write({
            'email_to': self.env.company.cancellation_tenancy_approval_id.partner_id.email,
            'email_from': self.tenant_id.email,
        })
        employee_mail_template.send_mail(self.id, force_send=True)
        thread_pool = self.sudo().env['mail.thread']
        thread_pool.message_notify(
            partner_ids=[self.env.company.cancellation_tenancy_approval_id.partner_id.id],
            subject=str('Tenant Tenancy'),
            body=str('This Tenant Tenancy ' + str(
                self.name) + 'in cancellation Requisition') + ' click here to open: <a target=_BLANK href="/web?#id=' + str(
                self.id) + '&view_type=form&model=tenant.tenancy&action=" style="font-weight: bold">' + str(
                self.name) + '</a>',
            email_from=self.env.user.company_id.catchall_formatted or self.env.user.company_id.email_formatted, )

    def button_set_to_renew(self):
        """
        This Method is used to open Tenancy renew wizard.
        @param self: The object pointer
        @return: Dictionary of values.
        """
        self.ensure_one()
        rent_schedule_obj = self.env['tenancy.rent.schedule']
        for tenancy_brw in self:
            if rent_schedule_obj.search([('tenancy_id', '=', tenancy_brw.id), ('move_check', '=', False)]):
                raise Warning(_('In order to Renew a Tenancy, Please make all related Rent Schedule entries posted.'))
        return {
            'name': _('Tenancy Renew Wizard'),
            'res_model': 'renew.tenancy',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {'default_start_date': self.date_start}
        }

    @api.model
    def cron_property_states_changed(self):
        """
        This Method is called by Scheduler for change property state
        according to tenancy state.
        @param self: The object pointer
        """
        # curr_date = datetime.now().date()
        # tncy_rec = self.search([('date_start', '<=', curr_date), ('date', '>=', curr_date), ('state', '=', 'open'), ('is_property', '=', True)])
        return True

    @api.model
    def cron_property_tenancy(self):
        """
        This Method is called by Scheduler to send email
        to tenant as a reminder for rent payment.
        @param self: The object pointer
        """
        due_date = datetime.now().date() + relativedelta(days=7)
        tncy_ids = self.search([('is_property', '=', True), ('state', '=', 'open')])
        rent_schedule_obj = self.env['tenancy.rent.schedule']
        model_data_id = self.env.ref('iwesabe_ppmdc_airport_management.property_email_template')
        for tncy_data in tncy_ids:
            tncy_rent_ids = rent_schedule_obj.search([('tenancy_id', '=', tncy_data.id), ('start_date', '=', due_date)])
            for tenancy in tncy_rent_ids:
                model_data_id.send_mail(tenancy.id, force_send=True, raise_exception=False)
        return True

    @api.model
    def send_mail_notification_tenant(self):
        for rec in self.search([]):
            today_date = datetime.strptime(str(date.today()), '%Y-%m-%d').date()
            if rec.date_end:
                end_date = datetime.strptime(str(rec.date_end), '%Y-%m-%d').date()
                diff = end_date - today_date
                if rec.tenant_id and float(diff.days) == 15:
                    employee_mail_template = self.env.ref('iwesabe_ppmdc_airport_management.email_send_to_tenancy_partner')
                    # employee_mail_template.sudo().send_mail(rec.id)
                    for user in rec.env.ref('iwesabe_ppmdc_airport_management.group_property_agent').users:
                        employee_mail_template.write({'email_to': user.partner_id.email, 'email_from': rec.tenant_id.email})
                        employee_mail_template.send_mail(rec.id, force_send=True)
                        thread_pool = self.sudo().env['mail.thread']
                        thread_pool.message_notify(
                            partner_ids=[user.partner_id.id],
                            subject=str('Tenant Tenancy'),
                            body=str('This Tenant Tenancy ' + str(
                                rec.name) + ' will ended after 15 days') + ' click here to open: <a target=_BLANK href="/web?#id=' + str(
                                rec.id) + '&view_type=form&model=tenant.tenancy&action=" style="font-weight: bold">' + str(
                                rec.name) + '</a>',
                            email_from=self.env.user.company_id.catchall_formatted or self.env.user.company_id.email_formatted, )

                    for user in rec.env.ref('iwesabe_ppmdc_airport_management.group_property_manager').users:
                        employee_mail_template.write({
                            'email_to': user.partner_id.email,
                            'email_from': rec.tenant_id.email,
                        })
                        employee_mail_template.send_mail(rec.id, force_send=True)
                        thread_pool = self.sudo().env['mail.thread']
                        thread_pool.message_notify(
                            partner_ids=[user.partner_id.id],
                            subject=str('Tenant Tenancy'),
                            body=str('This Tenant Tenancy ' + str(
                                rec.name) + ' will ended after 15 days') + ' click here to open: <a target=_BLANK href="/web?#id=' + str(
                                rec.id) + '&view_type=form&model=tenant.tenancy&action=" style="font-weight: bold">' + str(
                                rec.name) + '</a>',
                            email_from=self.env.user.company_id.catchall_formatted or self.env.user.company_id.email_formatted, )

                    for user in rec.env.ref('iwesabe_ppmdc_airport_management.group_property_owner').users:
                        employee_mail_template.write({
                            'email_to': user.partner_id.email,
                            'email_from': rec.tenant_id.email,
                        })
                        employee_mail_template.send_mail(rec.id, force_send=True)

                        thread_pool = self.sudo().env['mail.thread']
                        thread_pool.message_notify(
                            partner_ids=[user.partner_id.id],
                            subject=str('Tenant Tenancy'),
                            body=str('This Tenant Tenancy ' + str(
                                rec.name) + ' will ended after 15 days') + ' click here to open: <a target=_BLANK href="/web?#id=' + str(
                                rec.id) + '&view_type=form&model=tenant.tenancy&action=" style="font-weight: bold">' + str(
                                rec.name) + '</a>',
                            email_from=self.env.user.company_id.catchall_formatted or self.env.user.company_id.email_formatted, )
                    for user in rec.env.ref('iwesabe_ppmdc_airport_management.group_property_user').users:
                        employee_mail_template.write({
                            'email_to': user.partner_id.email,
                            'email_from': rec.tenant_id.email,
                        })
                        employee_mail_template.send_mail(rec.id, force_send=True)
                        thread_pool = self.sudo().env['mail.thread']
                        thread_pool.message_notify(
                            partner_ids=[user.partner_id.id],
                            subject=str('Tenant Tenancy'),
                            body=str('This Tenant Tenancy ' + str(
                                rec.name) + ' will ended after 15 days') + ' click here to open: <a target=_BLANK href="/web?#id=' + str(
                                rec.id) + '&view_type=form&model=tenant.tenancy&action=" style="font-weight: bold">' + str(
                                rec.name) + '</a>',
                            email_from=self.env.user.company_id.catchall_formatted or self.env.user.company_id.email_formatted, )

    def create_rent_schedule(self):
        """
        This button method is used to create rent schedule Lines.
        @param self: The object pointer
        """
        rent_obj = self.env['tenancy.rent.schedule']
        for tenancy_rec in self:
            if tenancy_rec.rent_type_id.renttype == 'Weekly':
                d1 = tenancy_rec.date_start
                d2 = tenancy_rec.date
                interval = int(tenancy_rec.rent_type_id.name)
                if d2 < d1:
                    raise Warning(
                        _('End date must be greater than start date.'))
                wek_diff = (d2 - d1)
                wek_tot1 = (wek_diff.days) / (interval * 7)
                wek_tot = (wek_diff.days) % (interval * 7)
                if wek_diff.days == 0:
                    wek_tot = 1
                if wek_tot1 > 0:
                    for wek_rec in range(int(wek_tot1)):
                        rent_obj.create(
                            {'start_date': d1,
                             'amount': tenancy_rec.rent * interval or 0.0,
                             'tenancy_id': tenancy_rec.id,
                             'currency_id': tenancy_rec.currency_id and tenancy_rec.currency_id.id or False,
                             'rel_tenant_id': tenancy_rec.tenant_id.id
                             })
                        d1 = d1 + relativedelta(days=(7 * interval))
                if wek_tot > 0:
                    one_day_rent = 0.0
                    if tenancy_rec.rent:
                        one_day_rent = (tenancy_rec.rent) / (7 * interval)
                    rent_obj.create(
                        {'start_date': d1.strftime(
                            DEFAULT_SERVER_DATE_FORMAT),
                         'amount': (one_day_rent * (wek_tot)) or 0.0,
                         'property_id': tenancy_rec.property_id and tenancy_rec.property_id.id or False,
                         'tenancy_id': tenancy_rec.id,
                         'currency_id': tenancy_rec.currency_id.id or False,
                         'rel_tenant_id': tenancy_rec.tenant_id.id
                         })
            elif tenancy_rec.rent_type_id.renttype != 'Weekly':
                if tenancy_rec.rent_type_id.renttype == 'Monthly':
                    interval = int(tenancy_rec.rent_type_id.name)
                if tenancy_rec.rent_type_id.renttype == 'Yearly':
                    interval = int(tenancy_rec.rent_type_id.name) * 12
                d1 = tenancy_rec.date_start
                d2 = tenancy_rec.date
                diff = abs((d1.year - d2.year) * 12 + (d1.month - d2.month))
                tot_rec = diff / interval
                tot_rec2 = diff % interval
                if abs(d1.month - d2.month) >= 0 and d1.day < d2.day:
                    tot_rec2 += 1
                if diff == 0:
                    tot_rec2 = 1
                if tot_rec > 0:
                    for rec in range(int(tot_rec)):
                        rent_obj.create(
                            {'start_date': d1,
                             'amount': tenancy_rec.rent * interval or 0.0,
                             'property_id': tenancy_rec.property_id and tenancy_rec.property_id.id or False,
                             'tenancy_id': tenancy_rec.id,
                             'currency_id': tenancy_rec.currency_id.id or False,
                             'rel_tenant_id': tenancy_rec.tenant_id.id
                             })
                        d1 = d1 + relativedelta(months=interval)
                if tot_rec2 > 0:
                    rent_obj.create({
                        'start_date': d1,
                        'amount': tenancy_rec.rent * tot_rec2 or 0.0,
                        'property_id': tenancy_rec.property_id and tenancy_rec.property_id.id or False,
                        'tenancy_id': tenancy_rec.id,
                        'currency_id': tenancy_rec.currency_id.id or False,
                        'rel_tenant_id': tenancy_rec.tenant_id.id
                    })
            return tenancy_rec.write({'rent_entry_chck': True})

    def button_cancel_tenancy(self):

        for record in self:
            record.write({'state': 'cancelled', 'tenancy_cancelled': True})
            rent_ids = self.env['tenancy.rent.schedule'].search([('tenancy_id', '=', record.id), ('paid', '=', False), ('move_check', '=', False)])
            for value in rent_ids:
                value.write({'is_readonly': True})

            employee_mail_template = self.env.ref('iwesabe_ppmdc_airport_management.email_send_to_tenancy_partner_cancelled')
            for user in self.env.ref('account.group_account_user').users:

                employee_mail_template.write({
                    'email_to': user.partner_id.email,
                    'email_from': record.tenant_id.email,
                })
                employee_mail_template.send_mail(self.id, force_send=True)

                thread_pool = self.sudo().env['mail.thread']
                thread_pool.message_notify(
                    partner_ids=[user.partner_id.id],
                    subject=str('Tenant Tenancy'),
                    body=str('This Tenant Tenancy ' + str(
                        record.name) + 'is cancelled') + ' click here to open: <a target=_BLANK href="/web?#id=' + str(
                        record.id) + '&view_type=form&model=tenant.tenancy&action=" style="font-weight: bold">' + str(
                        record.name) + '</a>',
                    email_from=self.env.user.company_id.catchall_formatted or self.env.user.company_id.email_formatted, )

        return True

    def create_invoice(self):
        """
        Create invoice for Rent Schedule.
        @param self: The object pointer
        """
        inv_obj = self.env['account.move']
        for rec in self:
            invoice_line = []
            for line in self.property_ids:
                invoice_line.append((0, 0, line._prepare_invoice_line()))
            invoice_vals = {
                'ref': self.name or '',
                'move_type': 'out_invoice',
                'partner_id': self.tenant_id.id,
                # 'journal_id': journal.id,  # company comes from the journal
                'invoice_origin': self.name,
                'invoice_line_ids': invoice_line,
                'company_id': self.company_id.id,
                'tenancy_id': rec.id or False,
                'invoice_date': fields.Date.today()

            }

            invoice_id = inv_obj.create(invoice_vals)
            inv_form_id = self.env.ref('account.view_move_form').id

        return {
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_id': inv_form_id,
            'res_id': invoice_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_move_type': 'out_invoice',
            'create': 0
        }
        action['context'] = context
        return action

    def action_create_service_application(self):
        return {
            'res_model': 'service.application',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('iwesabe_ppmdc_airport_management.service_application_form').id,
            'view_mode': 'form',
            'context': {'default_tenancy_id': self.id}
        }

    def action_view_service_application(self):
        actions = self.env.ref('iwesabe_ppmdc_airport_management.action_service_application').read()[0]
        actions['domain'] = [('id', '=', self.service_application_id.id)]
        actions['context'] = {'create': False, 'default_tenancy_id': self.id}
        return actions

    # @api.constrains('date_order')
    # def _check_date_order(self):
    #     for record in self:
    #         # check = any(r.date_from <= record.date_order and r.date_to >= record.date_order for r in record.rent_type_id.season_year_ids )
    #         for r in record.rent_type_id.season_year_ids:
    #             if not (r.date_from <= record.date_order and r.date_to >= record.date_order):
    #                 raise ValidationError(_('Order Date Invalid, not in rent season date!!'))

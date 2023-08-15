from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
from datetime import datetime
import pytz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

BILLING_PRICE_TOTAL_MAP = {
    'term_facilities_utilization': 'term_facilities_utilization_total',
    'systems': 'systems_total',
    '400hz': 'field_400_hz_total',
    'ground_handling': 'ground_handling_total',
    'aircraft_parking_not_registered': 'aircraft_parking_not_registered_total',
    'aircraft_registered': 'aircraft_registered_total',
    'PLBs_busses': 'plb_busses_total',
    'security_services': 'security_services_total',
    'bus_transportation': 'bus_transportation',
}


class AccountMove(models.Model):
    _inherit = 'account.move'

    appendix_id = fields.Many2one("invoice.appendix", string="Appendix Invoice", readonly=True, states={'draft': [('readonly', False)]})
    total_in_words_eng = fields.Char(string="Amount in Words",  compute='get_total_in_words')
    customer_contact_id = fields.Many2one("res.partner", string="Customer/Vendor Contact", readonly=True, states={'draft': [('readonly', False)]})
    contract_ref = fields.Char(string="Contract Reference", readonly=True, states={'draft': [('readonly', False)]})
    invoice_details = fields.Char(string="Invoice Type", readonly=True, states={'draft': [('readonly', False)]})
    partner_contacts_ids = fields.One2many("res.partner", string="", related="partner_id.child_ids")
    customer_code = fields.Char(string="Customer/Vendor Code", compute='get_customer_code', store=True)

    invoice_date = fields.Date(string='Invoice/Bill Date', readonly=True, index=True, copy=False,
                               states={'draft': [('readonly', False)]}, default=fields.Date.context_today)
    appendix_another_customer = fields.Boolean(string="")
    amount_discount = fields.Float('amount discount ')  # this field added to make upgrade for this module in the server only.

    airline_services_contract_id = fields.Many2one("airline.service.contract", string="Airline Services Contract",)
    is_services_contract = fields.Boolean()
    revenue_id = fields.Many2one('revenue.appendix', string="Revenue Appendix")

    @api.depends('partner_id')
    def get_customer_code(self):
        for rec in self:
            rec.customer_code = ''
            if rec.partner_id.ref:
                rec.customer_code = rec.partner_id.ref

    @api.onchange('partner_id')
    def get_filter_contact(self):
        return {'domain': {'customer_contact_id': [('id', 'in', self.partner_id.child_ids.ids)]}}

    @api.depends('amount_total', 'total_in_words_eng')
    def get_total_in_words(self):
        self.total_in_words_eng = str(self.currency_id.amount_to_text(self.amount_total)) + str(' ') + str('Only ')


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    tax_amount = fields.Float(string="Tax Amount",  compute='get_tax_amount')

    @api.depends('price_subtotal', 'price_total')
    def get_tax_amount(self):
        for rec in self:
            rec.tax_amount = 0.0
            if rec.move_id.move_type == 'out_invoice':
                rec.tax_amount = round(rec.price_total - rec.price_subtotal, 2)
            if rec.move_id.move_type == 'out_refund':
                rec.tax_amount = round(-(rec.price_total - rec.price_subtotal), 2)


class InvoiceAppendix(models.Model):
    _name = 'invoice.appendix'
    _rec_name = 'name'
    _description = 'Appendix Invoice'

    @api.model
    def _get_default_company(self):
        return self.env.company.id

    number = fields.Char(string="Number", default="New")
    name = fields.Char(string="Name", compute='get_name_description')
    from_date = fields.Date(string="Form Date", required=True)
    to_date = fields.Date(string="To Date", required=True)
    partner_id = fields.Many2one("res.partner", string="Partner", domain=[('is_airline', '=', True)], required=True)
    invoice_appendix_line_ids = fields.One2many("invoice.appendix.line", "invoice_appendix_id", string="")
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('done', 'Done'), ('cancel', 'Cancel')], string="Status", default='draft')

    # Totals
    term_facilities_utilization_total = fields.Float(string="Terminal Facilities Utilization", compute='get_total', store=True)
    systems_total = fields.Float(string="systems",  compute='get_total', store=True)
    field_400_hz_total = fields.Float(string="400hz",  compute='get_total', store=True)
    ground_handling_total = fields.Float(string="Ground Handling",  compute='get_total', store=True)
    aircraft_parking_not_registered_total = fields.Float(string="Aircraft Parking Not Registered", compute='get_total', store=True)
    aircraft_registered_total = fields.Float(string="Aircraft Registered",  compute='get_total', store=True)
    plb_busses_total = fields.Float(string="PLB’s & Busses",  compute='get_total', store=True)
    security_services_total = fields.Float(string="Security Services",  compute='get_total', store=True)
    bus_transportation = fields.Float(string="Buss Transportation",  compute='get_total', store=True)
    fees_total_total = fields.Float(string="Total",  compute='get_total', store=True)

    invoice_count = fields.Integer(string="", compute='get_invoices_count')
    invoice_count_other_customer = fields.Integer(string="", compute='get_invoices_count_other_customer')

    company_id = fields.Many2one("res.company", string="Company", default=_get_default_company)
    revenue_id = fields.Many2one("revenue.appendix", string="Revenue Appendix")

    billing_pricing_ids = fields.Many2many(comodel_name='billing.pricing', string='Related Bill Pricing',
                                           compute='_compute_billing_pricing_ids', store=True)

    is_gmt_customer = fields.Boolean(related="partner_id.is_gmt_customer", store=True)

    @api.depends('partner_id')
    def _compute_billing_pricing_ids(self):
        for invoice in self:
            if not invoice.partner_id:
                invoice.billing_pricing_ids = []
                continue
            pricing = self.env['billing.pricing']
            billing_domain = [('allow_other_customer', '=', False)]
            partner_billing_domain = [('airline_partner_ids', 'in', invoice.partner_id.id), ('allow_other_customer', '=', False)]
            partner_billing_ids = pricing.search(partner_billing_domain)
            types = list(set(partner_billing_ids.mapped('type')))
            if types:
                billing_domain += [('type', 'not in', types)]
            billing_domain += [('airline_partner_ids', '=', False)]
            billing_ids = pricing.search(billing_domain)
            dynamic_line_field_ids = pricing.with_context(active_test=False).search([]).mapped(
                'appendix_compute_field')
            invoice.billing_pricing_ids = [(6, 0, (partner_billing_ids + billing_ids).ids)]
            field_vals = {}
            for field_name in dynamic_line_field_ids.mapped('name'):
                field_vals[field_name] = False
            for field_name in (partner_billing_ids + billing_ids).mapped('appendix_compute_field.name'):
                field_vals[field_name] = True
            invoice.update(field_vals)

    @api.model
    def create(self, vals):
        if vals.get('number', _('New')) == _('New'):
            vals['number'] = self.env['ir.sequence'].next_by_code('invoice.appendix') or _('New')
        res = super(InvoiceAppendix, self).create(vals)
        return res

    def unlink(self):
        # delete from lines
        for res in self:
            for line in self.env['revenue.appendix.line'].search([('invoice_id', '=', res.id)]):
                line.check_depens_invoice()
        return super(InvoiceAppendix, self).unlink()

    def send_mail_appendix_and_invoice(self):
        # data = {
        #     'date_start': company.date_start,
        #     # 'date_end': company.date_end,
        #     'date_end': datetime.today(),
        #     'company_id': company.id,
        #     # 'partner_ids': [43],
        #     'show_aging_buckets': company.show_aging_buckets,
        #     'filter_non_due_partners': False,
        #     'account_type': company.account_type,
        #     'show_credit_limit': company.show_credit_limit,
        #     'aging_type': company.aging_type,
        #     'filter_negative_balances': False
        # }
        attachment_ids = []
        message = _(
            "<p>Dear %s,<br/><br/>Here is the invoice appendix and customer invoice attaches.</p>") % (
                      self.partner_id.name)
        partner_names = '<br />'
        index = 0
        index += 1
        # data['partner_ids'] = self._ids
        partner_names += '<p>%s: %s </p>' % (index, self.name)
        mail_values = {
            'subject': _('Invoice Appendix and Customer Invoice'),
            # 'body_html': message,
            'author_id': self.env.user.partner_id.id,
            'email_from': self.env.company.email or self.env.user.email_formatted,
            'email_to': self.partner_id.email,
            # 'attachment_ids': [(4, receipt.id)],
        }

        # invoice appendix report
        # invoice_appendix_report = self.env.ref(
        #     'iwesabe_billing_system.invoice_appendix_report_xlsx').report_action(self, data=None)
        # filename = 'Invoice Appendix_{}'.format(self.partner_id.name) + '.xlsx'
        # attachment_1 = self.env['ir.attachment'].create({
        #     'name': filename,
        #     'type': 'binary',
        #     'datas': base64.encodestring(invoice_appendix_report[0]),
        #     'store_fname': filename,
        #     'res_model': 'invoice.appendix',
        #     'res_id': self.id,
        #     'mimetype': 'application/vnd.ms-excel'
        # })
        # attachment_ids.append(attachment_1.id)

        # invoice appendix report
        invoice_appendix_report2 = self.env.ref(
            'iwesabe_billing_system.appendix_invoice_reports_pdf')._render_qweb_pdf(self.id, data=None)
        filename = 'Invoice Appendix_{}'.format(self.partner_id.name) + '.pdf'
        attachment_1 = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(invoice_appendix_report2[0]),
            'store_fname': filename,
            'res_model': 'invoice.appendix',
            'res_id': self.id,
            'mimetype': 'application/x-pdf'
        })
        attachment_ids.append(attachment_1.id)

        invoices = self.env['account.move'].search([('appendix_id', '=', self.id)], limit=1)
        invoice = False
        for rec in invoices:
            invoice = rec

        # Statement of Account
        customer_invoice = self.env.ref('iwesabe_billing_system.appendix_invoice_reports')._render_qweb_pdf(invoice.id, data=None)
        filename = 'Customer Invoice related_{}'.format(self.partner_id.name) + '.pdf'
        attachment_2 = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(customer_invoice[0]),
            'store_fname': filename,
            'res_model': 'account.move',
            'res_id': invoice.id,
            'mimetype': 'application/x-pdf'
        })
        attachment_ids.append(attachment_2.id)
        mail_values['body_html'] = message + partner_names + '<br />'
        outgoing_id = self.env['ir.mail_server'].sudo().search([('use_in_mail', '=', True)], limit=1)
        mail_values['mail_server_id'] = outgoing_id.id
        mail_values['attachment_ids'] = [(6, 0, attachment_ids)]
        mail = self.env['mail.mail'].sudo().create(mail_values)
        mail.send()

    def action_invoice_appendix_send(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            if self.partner_id.invoice_peendix_by_mail == 'pdf':
                template_id = ir_model_data.get_object_reference("iwesabe_billing_system",
                                                                 'email_template_invoice_appendix_template_pdf')[1]
            else:
                template_id = ir_model_data.get_object_reference("iwesabe_billing_system", 'email_template_invoice_appendix_template')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'invoice.appendix',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'proforma': self.env.context.get('proforma', True),
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def _get_gmt_time(self, fight_date):
        tz = pytz.timezone('GMT')
        fight_date = pytz.utc.localize(datetime.strptime(str(fight_date), DATETIME_FORMAT)).astimezone(tz).replace(tzinfo=None)
        return fight_date

    def action_compute(self):
        self._check_dynamic_field_defined()
        self.invoice_appendix_line_ids = False
        date_domain = [('actual_a_time_date', '>=', self.from_date), ('actual_d_time_date', '<=', self.to_date)]
        ams_data = self.env['ams.data'].search(['|', ('arrival_airline', '=', self.partner_id.airline_code), ('departure_airline', '=', self.partner_id.airline_code)] + date_domain)
        airline_data = []
        serial_number_counter = 1
        serial_number_dic = {}
        for dt in ams_data:
            actual_a_time = datetime.strptime(str(dt.actual_a_time), "%Y-%m-%d %H:%M:%S")
            actual_a_time_gmt = self._get_gmt_time(actual_a_time)
            actual_d_time = datetime.strptime(str(dt.actual_d_time), "%Y-%m-%d %H:%M:%S")
            actual_d_time_gmt = self._get_gmt_time(actual_d_time)
            ground_time = (actual_d_time - actual_a_time)
            minute = ground_time.seconds / 60
            hour = minute / 60
            airline_code = self.partner_id and self.partner_id.airline_code or dt.airline
            last_updated_date = dt.write_date
            if dt.ams_id not in serial_number_dic:
                serial_number_dic.setdefault(dt.ams_id, serial_number_counter)
                serial_number_counter += 1
            if dt.arrival_flight_no and dt.departure_flight_no:
                airline_data.append((0, 0, {
                    'serial_number': serial_number_dic.get(dt.ams_id, 0),
                    'ams_id': dt.ams_id,
                    'last_updated_date': last_updated_date,
                    'actual_a_time': dt.actual_a_time,
                    'actual_d_time': dt.actual_d_time,
                    'actual_a_time_gmt': actual_a_time_gmt,
                    'actual_d_time_gmt': actual_d_time_gmt,
                    'mode': 'a',
                    'apron': dt.apron,
                    'parking_stand': dt.a_stand,
                    'aircraft_registration': dt.reg_no,
                    'actual_aircraft': dt.actual_aircraft,
                    'actual_category': dt.actual_category,
                    'amtow': dt.amtow,
                    'airline': airline_code,
                    'agha': dt.agha,
                    'flight_no': dt.arrival_flight_no,
                    'arrival_airline_to': dt.arrival_airline,
                    'departure_airline_from': dt.departure_airline,
                    'flight_type': dt.a_status,
                    'pax': dt.a_passenger_no,
                    'terminal': dt.a_terminal,
                    'counter': dt.check_in_counter,
                    'ground_time': hour,
                    'FLT_type': dt.AFLT_type,
                    'buss_pbb': dt.ABUSS,
                }))

                airline_data.append((0, 0, {
                    'serial_number': serial_number_dic.get(dt.ams_id, 0),
                    'ams_id': dt.ams_id,
                    'last_updated_date': last_updated_date,
                    'actual_a_time': dt.actual_a_time,
                    'actual_d_time': dt.actual_d_time,
                    'actual_a_time_gmt': actual_a_time_gmt,
                    'actual_d_time_gmt': actual_d_time_gmt,
                    'mode': 'd',
                    'apron': dt.apron,
                    'parking_stand': dt.d_stand,
                    'aircraft_registration': dt.reg_no,
                    'actual_aircraft': dt.actual_aircraft,
                    'actual_category': dt.actual_category,
                    'amtow': dt.amtow,
                    'airline': airline_code,
                    'agha': dt.agha,
                    'flight_no': dt.departure_flight_no,
                    'arrival_airline_to': dt.arrival_airline,
                    'departure_airline_from': dt.departure_airline,
                    'flight_type': dt.d_status,
                    'pax': dt.d_passenger_no,
                    'terminal': dt.d_terminal,
                    'counter': dt.check_in_counter,
                    'ground_time': hour,
                    'FLT_type': dt.DFLT_type,
                    'buss_pbb': dt.DBUSS,
                }))
            elif dt.arrival_flight_no and not dt.departure_flight_no:
                airline_data.append((0, 0, {
                    'serial_number': serial_number_dic.get(dt.ams_id, 0),
                    'ams_id': dt.ams_id,
                    'last_updated_date': last_updated_date,
                    'actual_a_time': dt.actual_a_time,
                    'actual_d_time': dt.actual_d_time,
                    'actual_a_time_gmt': actual_a_time_gmt,
                    'actual_d_time_gmt': actual_d_time_gmt,
                    'mode': 'a',
                    'apron': dt.apron,
                    'parking_stand': dt.a_stand,
                    'aircraft_registration': dt.reg_no,
                    'actual_aircraft': dt.actual_aircraft,
                    'actual_category': dt.actual_category,
                    'amtow': dt.amtow,
                    'airline': airline_code,
                    'agha': dt.agha,
                    'flight_no': dt.arrival_flight_no,
                    'arrival_airline_to': dt.arrival_airline,
                    'departure_airline_from': dt.departure_airline,
                    'flight_type': dt.a_status,
                    'pax': dt.a_passenger_no,
                    'terminal': dt.a_terminal,
                    'counter': dt.check_in_counter,
                    'ground_time': hour,
                    'FLT_type': dt.AFLT_type,
                    'buss_pbb': dt.ABUSS,
                }))
            elif not dt.arrival_flight_no and dt.departure_flight_no:
                airline_data.append((0, 0, {
                    'serial_number': serial_number_dic.get(dt.ams_id, 0),
                    'ams_id': dt.ams_id,
                    'last_updated_date': last_updated_date,
                    'actual_a_time': dt.actual_a_time,
                    'actual_d_time': dt.actual_d_time,
                    'actual_a_time_gmt': actual_a_time_gmt,
                    'actual_d_time_gmt': actual_d_time_gmt,
                    'mode': 'd',
                    'apron': dt.apron,
                    'parking_stand': dt.d_stand,
                    'aircraft_registration': dt.reg_no,
                    'actual_aircraft': dt.actual_aircraft,
                    'actual_category': dt.actual_category,
                    'amtow': dt.amtow,
                    'airline': airline_code,
                    'agha': dt.agha,
                    'flight_no': dt.departure_flight_no,
                    'arrival_airline_to': dt.arrival_airline,
                    'departure_airline_from': dt.departure_airline,
                    'flight_type': dt.d_status,
                    'pax': dt.d_passenger_no,
                    'terminal': dt.d_terminal,
                    'counter': dt.check_in_counter,
                    'ground_time': hour,
                    'FLT_type': dt.DFLT_type,
                    'buss_pbb': dt.DBUSS,
                }))
        if len(airline_data) > 0:
            self.invoice_appendix_line_ids = airline_data
        self._compute_billing_pricing_ids()
        self.invoice_appendix_line_ids.get_services()
        self._compute_dynamic_total_pricing()

    def action_confirm(self):
        self._check_dynamic_field_defined()
        self.write({'state': 'confirm'})

    def action_reset_draft(self):
        self.get_invoices_count()
        self.get_invoices_count_other_customer()
        if self.invoice_count == 0 and self.invoice_count_other_customer == 0:
            self.write({'state': 'draft'})
        else:
            raise UserError(_("Please delete Invoices related to this record"))

    def action_cancel(self):
        self.get_invoices_count()
        self.get_invoices_count_other_customer()
        if self.invoice_count == 0 and self.invoice_count_other_customer == 0:
            self.write({'state': 'cancel'})
        else:
            raise UserError(_("Please Cancel Invoices related to this record"))

    def _check_dynamic_field_defined(self):
        for invoice in self:
            billing_pricings = ', '.join(
                invoice.billing_pricing_ids.filtered(lambda b: not b.appendix_line_value_field).mapped('name'))
            if billing_pricings:
                raise UserError(_("Please configure dynamic fields for (%s)") % billing_pricings)

    @api.depends()
    def get_invoices_count(self):
        for res in self:
            self.invoice_count = self.env['account.move'].search_count([('appendix_id', '=', res.id), ('appendix_another_customer', '=', False)])

    @api.depends()
    def get_invoices_count_other_customer(self):
        self.invoice_count_other_customer = self.env['account.move'].search_count([('appendix_id', '=', self.id), ('appendix_another_customer', '=', True)])

    def action_open_related_invoices(self):
        return {
            'name': 'Invoices',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('appendix_id', '=', self.id), ('appendix_another_customer', '=', False)],
            'target': 'current',
        }

    def action_open_related_invoices_other_customer(self):
        return {
            'name': 'Invoices',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('appendix_id', '=', self.id), ('appendix_another_customer', '=', True)],
            'target': 'current',
        }

    @api.depends('invoice_appendix_line_ids')
    def get_total(self):
        for res in self:
            res.fees_total_total = 0.0
            res.term_facilities_utilization_total = 0.0
            res.systems_total = 0.0
            res.field_400_hz_total = 0.0
            res.ground_handling_total = 0.0
            res.aircraft_parking_not_registered_total = 0.0
            res.aircraft_registered_total = 0.0
            res.plb_busses_total = 0.0
            res.security_services_total = 0.0
            res.bus_transportation = 0.0
        self._compute_dynamic_total_pricing()

    def _compute_dynamic_total_pricing(self):
        field_vals = {}
        pricing_ids = self.env['billing.pricing'].with_context(active_test=False).search([])
        for field_name in pricing_ids.mapped('appendix_total_field.name'):
            field_vals[field_name] = 0.0
        for invoice in self:
            invoice.update(invoice._map_dynamic_billing_total_pricing(field_vals))

    def _map_dynamic_billing_total_pricing(self, default_fields):
        self.ensure_one()
        total_field_values = {}
        for pricing in self.mapped('billing_pricing_ids'):
            if not pricing.appendix_line_value_field:
                continue
            total = sum(self.mapped('invoice_appendix_line_ids').mapped(pricing.appendix_line_value_field.name))
            total_field_values.update({pricing.appendix_total_field.name: total})
            if pricing.type in BILLING_PRICE_TOTAL_MAP:
                total_field_values.update({BILLING_PRICE_TOTAL_MAP.get(pricing.type): total})
        fees_total_total = sum(total_field_values.values())
        total_field_values.update(fees_total_total=fees_total_total)
        return {
            **default_fields, **total_field_values
        }

    @api.depends('from_date', 'to_date', 'partner_id')
    def get_name_description(self):
        for res in self:
            res.name = ""
            res.name = 'Actual Traffic From ' + str(res.from_date) + ' to ' + str(res.to_date) + ' For ' + str(res.partner_id and res.partner_id.name or '') + ' ( ' + str(len(res.invoice_appendix_line_ids)) + ' ) Movements'

    def create_invoice_for_airline_customer_from_wiz(self, partner_id, system):
        if partner_id and len(system) == 0:
            return

        account_inv_obj = self.env['account.move']
        pricing = self.env['billing.pricing']

        term_facilities_utilization = systems = field_400_hz = ground_handling = aircraft_parking_not_registered = False
        plb_busses = security_services = bus_transportation = aircraft_registered = False
        if 'term_facilities_utilization' in system:
            term_facilities_utilization = pricing.search([('type', '=', 'term_facilities_utilization'), ('allow_other_customer', '=', False)], limit=1).product_id

        if 'systems' in system:
            systems = pricing.search([('type', '=', 'systems'), ('allow_other_customer', '=', False)], limit=1).product_id

        if 'field_400_hz' in system:
            field_400_hz = pricing.search([('type', '=', '400hz'), ('allow_other_customer', '=', False)], limit=1).product_id

        if 'ground_handling' in system:
            ground_handling = pricing.search([('type', '=', 'ground_handling'), ('allow_other_customer', '=', False)], limit=1).product_id

        if 'aircraft_parking_not_registered' in system:
            aircraft_parking_not_registered = pricing.search([('type', '=', 'aircraft_parking_not_registered'), ('allow_other_customer', '=', False)], limit=1).product_id

        if 'aircraft_registered' in system:
            aircraft_registered = pricing.search([('type', '=', 'aircraft_registered'), ('allow_other_customer', '=', False)], limit=1).product_id

        if 'plb_busses' in system:
            plb_busses = pricing.search([('type', '=', 'PLBs_busses'), ('allow_other_customer', '=', False)], limit=1).product_id

        if 'security_services' in system:
            security_services = pricing.search([('type', '=', 'security_services'), ('allow_other_customer', '=', False)], limit=1).product_id

        if 'bus_transportation' in system:
            bus_transportation = pricing.search([('type', '=', 'bus_transportation'), ('allow_other_customer', '=', False)], limit=1).product_id

        # Search for the income account
        if term_facilities_utilization:
            if term_facilities_utilization.property_account_income_id:
                term_facilities_utilization_account = term_facilities_utilization.property_account_income_id.id
            elif term_facilities_utilization.categ_id.property_account_income_categ_id:
                term_facilities_utilization_account = term_facilities_utilization.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                % (term_facilities_utilization.name, term_facilities_utilization.id))

        if systems:
            # Search for the income account
            if systems.property_account_income_id:
                systems_account = systems.property_account_income_id.id
            elif systems.categ_id.property_account_income_categ_id:
                systems_account = systems.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                % (systems.name, systems.id))
        if field_400_hz:
            if field_400_hz.property_account_income_id:
                field_400_hz_incom_account = field_400_hz.property_account_income_id.id
            elif systems.categ_id.property_account_income_categ_id:
                field_400_hz_incom_account = field_400_hz.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                % (field_400_hz.name, field_400_hz.id))
        if ground_handling:
            if ground_handling.property_account_income_id:
                ground_handling_account = ground_handling.property_account_income_id.id
            elif ground_handling.categ_id.property_account_income_categ_id:
                ground_handling_account = ground_handling.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                % (ground_handling.name, ground_handling.id))
        if aircraft_parking_not_registered:
            if aircraft_parking_not_registered.property_account_income_id:
                aircraft_parking_not_registered_account = aircraft_parking_not_registered.property_account_income_id.id
            elif aircraft_parking_not_registered.categ_id.property_account_income_categ_id:
                aircraft_parking_not_registered_account = aircraft_parking_not_registered.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                % (aircraft_parking_not_registered.name, aircraft_parking_not_registered.id))
        if aircraft_registered:
            if aircraft_registered.property_account_income_id:
                aircraft_registered_account = aircraft_registered.property_account_income_id.id
            elif aircraft_registered.categ_id.property_account_income_categ_id:
                aircraft_registered_account = aircraft_registered.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                % (aircraft_registered.name, aircraft_registered.id))
        if plb_busses:
            if plb_busses.property_account_income_id:
                plb_busses_account = plb_busses.property_account_income_id.id
            elif plb_busses.categ_id.property_account_income_categ_id:
                plb_busses_account = plb_busses.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                % (plb_busses.name, plb_busses.id))
        if security_services:
            if security_services.property_account_income_id:
                security_services_account = security_services.property_account_income_id.id
            elif security_services.categ_id.property_account_income_categ_id:
                security_services_account = security_services.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                % (security_services.name, security_services.id))

        if bus_transportation:
            if bus_transportation.property_account_income_id:
                bus_transportation_account = bus_transportation.property_account_income_id.id
            elif bus_transportation.categ_id.property_account_income_categ_id:
                bus_transportation_account = bus_transportation.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                % (bus_transportation.name, bus_transportation.id))

        invoice_appendix_perv = self.env['invoice.appendix'].search([('from_date', '=', self.from_date), ('to_date', '=', self.to_date), ('partner_id', '=', self.partner_id.id)])
        invoice_appendix_pervious = None
        if invoice_appendix_perv:
            for rec in invoice_appendix_perv:
                if rec != self:
                    invoice_appendix_pervious = rec

        if invoice_appendix_pervious:
            term_facilities_price = systems_price = field_400_hz_price = ground_handling_price = aircraft_parking_not_registered_price = aircraft_registered_price = plb_busses_price = security_services_price = bus_transportation_price = 0.0
            if term_facilities_utilization:
                term_facilities_price = sum(self.invoice_appendix_line_ids.mapped('term_facilities_utilization'))
            if systems:
                systems_price = sum(self.invoice_appendix_line_ids.mapped('systems'))
            if field_400_hz:
                field_400_hz_price = sum(self.invoice_appendix_line_ids.mapped('field_400_hz'))
            if ground_handling:
                ground_handling_price = sum(self.invoice_appendix_line_ids.mapped('ground_handling'))
            if aircraft_parking_not_registered:
                aircraft_parking_not_registered_price = sum(self.invoice_appendix_line_ids.mapped('aircraft_parking_not_registered'))
            if aircraft_registered:
                aircraft_registered_price = sum(self.invoice_appendix_line_ids.mapped('aircraft_registered'))
            if plb_busses:
                plb_busses_price = sum(self.invoice_appendix_line_ids.mapped('plb_busses'))
            if security_services:
                security_services_price = sum(self.invoice_appendix_line_ids.mapped('security_services'))
            if bus_transportation:
                bus_transportation_price = sum(self.invoice_appendix_line_ids.mapped('bus_transportation'))
            current_total = term_facilities_price + systems_price + field_400_hz_price + ground_handling_price + aircraft_parking_not_registered_price + aircraft_registered_price + plb_busses_price + security_services_price + bus_transportation_price

            # ///////////////////// Prev total //////////////////////////

            term_facilities_price_prev = systems_price_prev = field_400_hz_price_prev = ground_handling_price_prev = aircraft_parking_not_registered_price_prev = 0.0
            aircraft_registered_price_prev = plb_busses_price_prev = security_services_price_prev = bus_transportation_price_prev = 0.0
            if term_facilities_utilization:
                term_facilities_price_prev = sum(invoice_appendix_pervious.invoice_appendix_line_ids.mapped(
                    'term_facilities_utilization'))
            if systems:
                systems_price_prev = sum(
                    invoice_appendix_pervious.invoice_appendix_line_ids.mapped('systems'))
            if field_400_hz:
                field_400_hz_price_prev = sum(
                    invoice_appendix_pervious.invoice_appendix_line_ids.mapped('field_400_hz'))
            if ground_handling:
                ground_handling_price_prev = sum(
                    invoice_appendix_pervious.invoice_appendix_line_ids.mapped('ground_handling'))
            if aircraft_parking_not_registered:
                aircraft_parking_not_registered_price_prev = sum(
                    invoice_appendix_pervious.invoice_appendix_line_ids.mapped(
                        'aircraft_parking_not_registered'))
            if aircraft_registered:
                aircraft_registered_price_prev = sum(
                    invoice_appendix_pervious.invoice_appendix_line_ids.mapped('aircraft_registered'))
            if plb_busses:
                plb_busses_price_prev = sum(
                    invoice_appendix_pervious.invoice_appendix_line_ids.mapped('plb_busses'))
            if security_services:
                security_services_price_prev = sum(
                    invoice_appendix_pervious.invoice_appendix_line_ids.mapped('security_services'))
            if bus_transportation:
                bus_transportation_price_prev = sum(invoice_appendix_pervious.invoice_appendix_line_ids.mapped('bus_transportation'))
            prev_total = term_facilities_price_prev + systems_price_prev + field_400_hz_price_prev + ground_handling_price_prev + bus_transportation_price_prev
            prev_total += aircraft_parking_not_registered_price_prev + aircraft_registered_price_prev + plb_busses_price_prev + security_services_price_prev
            # //////////////////////////////////// difference ////////////////////////////////////////
            diff = current_total - prev_total
            if diff < 0:
                invoice_lines = []
                product_diff_credit_note = self.env['product.product'].search([('is_credit_note', '=', True)], limit=1)
                # Search for the income account
                if product_diff_credit_note.property_account_income_id:
                    product_diff_credit_note_account = product_diff_credit_note.property_account_income_id.id
                elif product_diff_credit_note.categ_id.property_account_income_categ_id:
                    product_diff_credit_note_account = product_diff_credit_note.categ_id.property_account_income_categ_id.id
                else:
                    raise UserError(_('Please define income '
                                      'account for this Service: "%s" (id:%d).')
                                    % (product_diff_credit_note.name, product_diff_credit_note.id))

                invoice_lines.append((0, 0, {
                    'name': str(product_diff_credit_note.name) + ' - ' + str('Credit note from appendix'),
                    'product_id': product_diff_credit_note.id,
                    'tax_ids': product_diff_credit_note.taxes_id.ids,
                    'account_id': product_diff_credit_note_account,
                    'price_unit': abs(diff)
                }))

                vals = {
                    'appendix_id': self.id,
                    'move_type': 'out_refund',
                    'invoice_date': self.from_date,
                    'invoice_date_due': self.from_date,
                    'date': self.from_date,
                    'invoice_origin': self.name,
                    'customer_contact_id': self.partner_id.child_ids[0] if self.partner_id.child_ids else False,
                    'partner_id': self.partner_id.id,
                    'invoice_user_id': self.env.user.id,
                    'invoice_line_ids': invoice_lines,
                }

                invoice_id = account_inv_obj.create(vals)
            else:
                # related_previouse_invoice = self.env['account.move'].search([('appendix_id', '=', invoice_appendix_pervious.id), ('appendix_another_customer', '=', False)], limit=1)
                # related_previouse_invoice.button_cancel()
                invoice_lines = []
                if term_facilities_utilization:
                    term_facilities_price = sum(self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped(
                        'term_facilities_utilization'))
                    if term_facilities_price > 0:
                        invoice_lines.append((0, 0, {
                            'name': term_facilities_utilization.name + str(' With Tax'),
                            'product_id': term_facilities_utilization.id,
                            'tax_ids': term_facilities_utilization.taxes_id.ids,
                            'account_id': term_facilities_utilization_account,
                            'price_unit': term_facilities_price
                        }))
                    term_facilities_price_without_vat = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped(
                            'term_facilities_utilization'))
                    if term_facilities_price_without_vat > 0:
                        invoice_lines.append((0, 0, {
                            'name': term_facilities_utilization.name,
                            'product_id': term_facilities_utilization.id,
                            'account_id': term_facilities_utilization_account,
                            'price_unit': term_facilities_price_without_vat
                        }))
                if systems:

                    systems_price = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('systems'))
                    if systems_price > 0:
                        invoice_lines.append((0, 0, {
                            'name': systems.name + str(' With Tax'),
                            'product_id': systems.id,
                            'tax_ids': systems.taxes_id.ids,
                            'account_id': systems_account,
                            'price_unit': systems_price
                        }))
                    systems_price_without_vat = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('systems'))
                    if systems_price_without_vat > 0:
                        invoice_lines.append((0, 0, {
                            'name': systems.name,
                            'product_id': systems.id,
                            'account_id': systems_account,
                            'price_unit': systems_price_without_vat
                        }))

                if field_400_hz:

                    field_400_hz_price = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('field_400_hz'))
                    if field_400_hz_price > 0:
                        invoice_lines.append((0, 0, {
                            'name': field_400_hz.name + str(' With Tax'),
                            'product_id': field_400_hz.id,
                            'tax_ids': field_400_hz.taxes_id.ids,
                            'account_id': field_400_hz_incom_account,
                            'price_unit': field_400_hz_price
                        }))
                    field_400_hz_price_without_vat = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('field_400_hz'))
                    if field_400_hz_price_without_vat > 0:
                        invoice_lines.append((0, 0, {
                            'name': field_400_hz.name,
                            'product_id': field_400_hz.id,
                            'account_id': field_400_hz_incom_account,
                            'price_unit': field_400_hz_price_without_vat
                        }))
                if ground_handling:

                    ground_handling_price = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('ground_handling'))
                    if ground_handling_price > 0:
                        invoice_lines.append((0, 0, {
                            'name': ground_handling.name + str(' With Tax'),
                            'product_id': ground_handling.id,
                            'tax_ids': ground_handling.taxes_id.ids,
                            'account_id': ground_handling_account,
                            'price_unit': ground_handling_price
                        }))
                    ground_handling_price_without_tax = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('ground_handling'))
                    if ground_handling_price_without_tax > 0:
                        invoice_lines.append((0, 0, {
                            'name': ground_handling.name,
                            'product_id': ground_handling.id,
                            'account_id': ground_handling_account,
                            'price_unit': ground_handling_price_without_tax
                        }))

                if aircraft_parking_not_registered:
                    aircraft_parking_not_registered_price = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped(
                            'aircraft_parking_not_registered'))
                    if aircraft_parking_not_registered_price > 0:
                        invoice_lines.append((0, 0, {
                            'name': aircraft_parking_not_registered.name + str(' With Tax'),
                            'product_id': aircraft_parking_not_registered.id,
                            'tax_ids': aircraft_parking_not_registered.taxes_id.ids,
                            'account_id': aircraft_parking_not_registered_account,
                            'price_unit': aircraft_parking_not_registered_price
                        }))
                    aircraft_parking_not_registered_price_without_tax = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped(
                            'aircraft_parking_not_registered'))
                    if aircraft_parking_not_registered_price_without_tax > 0:
                        invoice_lines.append((0, 0, {
                            'name': aircraft_parking_not_registered.name,
                            'product_id': aircraft_parking_not_registered.id,
                            'account_id': aircraft_parking_not_registered_account,
                            'price_unit': aircraft_parking_not_registered_price_without_tax
                        }))

                if aircraft_registered:

                    aircraft_registered_price = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('aircraft_registered'))
                    if aircraft_registered_price > 0:
                        invoice_lines.append((0, 0, {
                            'name': aircraft_registered.name + str(' With Tax'),
                            'product_id': aircraft_registered.id,
                            'tax_ids': aircraft_registered.taxes_id.ids,
                            'account_id': aircraft_registered_account,
                            'price_unit': aircraft_registered_price
                        }))
                    aircraft_registered_price_without_tax = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('aircraft_registered'))
                    if aircraft_registered_price_without_tax > 0:
                        invoice_lines.append((0, 0, {
                            'name': aircraft_registered.name,
                            'product_id': aircraft_registered.id,
                            'account_id': aircraft_registered_account,
                            'price_unit': aircraft_registered_price_without_tax
                        }))

                if plb_busses:

                    plb_busses_price = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('plb_busses'))
                    if plb_busses_price > 0:
                        invoice_lines.append((0, 0, {
                            'name': plb_busses.name + str(' With Tax'),
                            'product_id': plb_busses.id,
                            'tax_ids': plb_busses.taxes_id.ids,
                            'account_id': plb_busses_account,
                            'price_unit': plb_busses_price
                        }))
                    plb_busses_price_without_tax = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('plb_busses'))
                    if plb_busses_price_without_tax > 0:
                        invoice_lines.append((0, 0, {
                            'name': plb_busses.name,
                            'product_id': plb_busses.id,
                            'account_id': plb_busses_account,
                            'price_unit': plb_busses_price_without_tax
                        }))
                if security_services:

                    security_services_price = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('security_services'))
                    if security_services_price > 0:
                        invoice_lines.append((0, 0, {
                            'name': security_services.name + str(' With Tax'),
                            'product_id': security_services.id,
                            'tax_ids': security_services.taxes_id.ids,
                            'account_id': security_services_account,
                            'price_unit': security_services_price
                        }))
                    security_services_price_without_tax = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('security_services'))
                    if security_services_price_without_tax > 0:
                        invoice_lines.append((0, 0, {
                            'name': security_services.name,
                            'product_id': security_services.id,
                            'tax_ids': security_services.taxes_id.ids,
                            'account_id': security_services_account,
                            'price_unit': security_services_price_without_tax
                        }))

                if bus_transportation:
                    bus_transportation_price = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('bus_transportation'))
                    if bus_transportation_price > 0:
                        invoice_lines.append((0, 0, {
                            'name': bus_transportation.name + str(' With Tax'),
                            'product_id': bus_transportation.id,
                            'tax_ids': bus_transportation.taxes_id.ids,
                            'account_id': bus_transportation_account,
                            'price_unit': bus_transportation_price
                        }))
                    bus_transportation_price_without_tax = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('bus_transportation'))
                    if bus_transportation_price_without_tax > 0:
                        invoice_lines.append((0, 0, {
                            'name': bus_transportation.name,
                            'product_id': bus_transportation.id,
                            'tax_ids': bus_transportation.taxes_id.ids,
                            'account_id': bus_transportation_account,
                            'price_unit': bus_transportation_price_without_tax
                        }))

                vals = {
                    'appendix_id': self.id,
                    'move_type': 'out_invoice',
                    'invoice_date': fields.Date.today(),
                    'invoice_date_due': fields.Date.today(),
                    'date': self.from_date,
                    'invoice_origin': self.name,
                    'customer_contact_id': self.partner_id.child_ids[0] if self.partner_id.child_ids else False,
                    'partner_id': self.partner_id.id,
                    'invoice_user_id': self.env.user.id,
                    'invoice_line_ids': invoice_lines,
                }
                # invoice created
                account_inv_obj.create(vals)

        else:
            invoice_lines = []
            if term_facilities_utilization:
                term_facilities_price = sum(self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('term_facilities_utilization'))
                if term_facilities_price > 0:
                    invoice_lines.append((0, 0, {
                        'name': term_facilities_utilization.name + str(' With Tax'),
                        'product_id': term_facilities_utilization.id,
                        'tax_ids': term_facilities_utilization.taxes_id.ids,
                        'account_id': term_facilities_utilization_account,
                        'price_unit': term_facilities_price
                    }))
                term_facilities_price_without_vat = sum(self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('term_facilities_utilization'))
                if term_facilities_price_without_vat > 0:
                    invoice_lines.append((0, 0, {
                        'name': term_facilities_utilization.name,
                        'product_id': term_facilities_utilization.id,
                        'account_id': term_facilities_utilization_account,
                        'price_unit': term_facilities_price_without_vat
                    }))
            if systems:
                systems_price = sum(self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('systems'))
                if systems_price > 0:
                    invoice_lines.append((0, 0, {
                        'name': systems.name + str(' With Tax'),
                        'product_id': systems.id,
                        'tax_ids': systems.taxes_id.ids,
                        'account_id': systems_account,
                        'price_unit': systems_price
                    }))
                systems_price_without_vat = sum(self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('systems'))
                if systems_price_without_vat > 0:
                    invoice_lines.append((0, 0, {
                        'name': systems.name,
                        'product_id': systems.id,
                        'account_id': systems_account,
                        'price_unit': systems_price_without_vat
                    }))

            if field_400_hz:

                field_400_hz_price = sum(self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('field_400_hz'))
                if field_400_hz_price > 0:
                    invoice_lines.append((0, 0, {
                        'name': field_400_hz.name + str(' With Tax'),
                        'product_id': field_400_hz.id,
                        'tax_ids': field_400_hz.taxes_id.ids,
                        'account_id': field_400_hz_incom_account,
                        'price_unit': field_400_hz_price
                    }))
                field_400_hz_price_without_vat = sum(self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('field_400_hz'))
                if field_400_hz_price_without_vat > 0:
                    invoice_lines.append((0, 0, {
                        'name': field_400_hz.name,
                        'product_id': field_400_hz.id,
                        'account_id': field_400_hz_incom_account,
                        'price_unit': field_400_hz_price_without_vat
                    }))
            if ground_handling:
                ground_handling_price = sum(self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('ground_handling'))
                if ground_handling_price > 0:
                    invoice_lines.append((0, 0, {
                        'name': ground_handling.name + str(' With Tax'),
                        'product_id': ground_handling.id,
                        'tax_ids': ground_handling.taxes_id.ids,
                        'account_id': ground_handling_account,
                        'price_unit': ground_handling_price
                    }))
                ground_handling_price_without_tax = sum(self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('ground_handling'))
                if ground_handling_price_without_tax > 0:
                    invoice_lines.append((0, 0, {
                        'name': ground_handling.name,
                        'product_id': ground_handling.id,
                        'account_id': ground_handling_account,
                        'price_unit': ground_handling_price_without_tax
                    }))

            if aircraft_parking_not_registered:

                aircraft_parking_not_registered_price = sum(self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('aircraft_parking_not_registered'))
                if aircraft_parking_not_registered_price > 0:
                    invoice_lines.append((0, 0, {
                        'name': aircraft_parking_not_registered.name + str(' With Tax'),
                        'product_id': aircraft_parking_not_registered.id,
                        'tax_ids': aircraft_parking_not_registered.taxes_id.ids,
                        'account_id': aircraft_parking_not_registered_account,
                        'price_unit': aircraft_parking_not_registered_price
                    }))
                aircraft_parking_not_registered_price_without_tax = sum(self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('aircraft_parking_not_registered'))
                if aircraft_parking_not_registered_price_without_tax > 0:
                    invoice_lines.append((0, 0, {
                        'name': aircraft_parking_not_registered.name,
                        'product_id': aircraft_parking_not_registered.id,
                        'account_id': aircraft_parking_not_registered_account,
                        'price_unit': aircraft_parking_not_registered_price_without_tax
                    }))

            if aircraft_registered:

                aircraft_registered_price = sum(self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('aircraft_registered'))
                if aircraft_registered_price > 0:
                    invoice_lines.append((0, 0, {
                        'name': aircraft_registered.name + str(' With Tax'),
                        'product_id': aircraft_registered.id,
                        'tax_ids': aircraft_registered.taxes_id.ids,
                        'account_id': aircraft_registered_account,
                        'price_unit': aircraft_registered_price
                    }))
                aircraft_registered_price_without_tax = sum(
                    self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('aircraft_registered'))
                if aircraft_registered_price_without_tax > 0:
                    invoice_lines.append((0, 0, {
                        'name': aircraft_registered.name,
                        'product_id': aircraft_registered.id,
                        'account_id': aircraft_registered_account,
                        'price_unit': aircraft_registered_price_without_tax
                    }))

            if plb_busses:

                plb_busses_price = sum(self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('plb_busses'))
                if plb_busses_price > 0:
                    invoice_lines.append((0, 0, {
                        'name': plb_busses.name + str(' With Tax'),
                        'product_id': plb_busses.id,
                        'tax_ids': plb_busses.taxes_id.ids,
                        'account_id': plb_busses_account,
                        'price_unit': plb_busses_price
                    }))
                plb_busses_price_without_tax = sum(
                    self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('plb_busses'))
                if plb_busses_price_without_tax > 0:
                    invoice_lines.append((0, 0, {
                        'name': plb_busses.name,
                        'product_id': plb_busses.id,
                        'account_id': plb_busses_account,
                        'price_unit': plb_busses_price_without_tax
                    }))
            if security_services:

                security_services_price = sum(self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('security_services'))
                if security_services_price > 0:
                    invoice_lines.append((0, 0, {
                        'name': security_services.name + str(' With Tax'),
                        'product_id': security_services.id,
                        'tax_ids': security_services.taxes_id.ids,
                        'account_id': security_services_account,
                        'price_unit': security_services_price
                    }))
                security_services_price_without_tax = sum(
                    self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('security_services'))
                if security_services_price_without_tax > 0:
                    invoice_lines.append((0, 0, {
                        'name': security_services.name,
                        'product_id': security_services.id,
                        'tax_ids': security_services.taxes_id.ids,
                        'account_id': security_services_account,
                        'price_unit': security_services_price_without_tax
                    }))

            if bus_transportation:

                bus_transportation_price = sum(self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('bus_transportation'))
                if bus_transportation_price > 0:
                    invoice_lines.append((0, 0, {
                        'name': bus_transportation.name + str(' With Tax'),
                        'product_id': bus_transportation.id,
                        'tax_ids': bus_transportation.taxes_id.ids,
                        'account_id': bus_transportation_account,
                        'price_unit': bus_transportation_price
                    }))
                bus_transportation_price_without_tax = sum(
                    self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('bus_transportation'))
                if bus_transportation_price_without_tax > 0:
                    invoice_lines.append((0, 0, {
                        'name': bus_transportation.name,
                        'product_id': bus_transportation.id,
                        'tax_ids': bus_transportation.taxes_id.ids,
                        'account_id': bus_transportation_account,
                        'price_unit': bus_transportation_price_without_tax
                    }))

            vals = {
                'appendix_id': self.id,
                'move_type': 'out_invoice',
                'invoice_date': fields.Date.today(),
                'invoice_date_due': fields.Date.today(),
                'date': self.from_date,
                'invoice_origin': self.name,
                'customer_contact_id': self.partner_id.child_ids[0] if self.partner_id.child_ids else False,
                'partner_id': self.partner_id.id,
                'invoice_user_id': self.env.user.id,
                'invoice_line_ids': invoice_lines,
            }
            # invoice creating
            account_inv_obj.create(vals)
        if account_inv_obj:
            action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = account_inv_obj.id
            return action

    def create_invoice(self):
        wiz_id = self.env['invoice.customer'].create({
            'invoice_line_ids': [(0, 0, {'invoice_id': self.id, 'partner_id': self.partner_id.id})]
        })
        if wiz_id:
            return {
               'name': _('Appendix Invoice For Airline Customer'),
               'res_model': 'invoice.customer',
               'type': 'ir.actions.act_window',
               'view_mode': 'form',
               'view_type': 'form',
               'res_id': wiz_id.id,
               'target': 'new',
            }

    def create_invoice_for_another_customer(self):
        wiz_id = self.env['invoice.other.customer'].create({'invoice_appendix_id': self.id})
        if wiz_id:
            return {
               'name': _('Appendix Invoice For Other Customer'),
               'res_model': 'invoice.other.customer',
               'type': 'ir.actions.act_window',
               'view_mode': 'form',
               'view_type': 'form',
               'res_id': wiz_id.id,
               'target': 'new',
            }

    def create_invoice_for_another_customer_from_wiz(self, partner_id, system):
        if partner_id and len(system) == 0:
            return
        account_inv_obj = self.env['account.move']
        pricing = self.env['billing.pricing']
        term_facilities_utilization = systems = field_400_hz = ground_handling = aircraft_parking_not_registered = False
        aircraft_registered = plb_busses = security_services = bus_transportation = False

        if 'term_facilities_utilization' in system:
            term_facilities_utilization = pricing.search([('type', '=', 'term_facilities_utilization'), ('allow_other_customer', '=', True)], limit=1).product_id
        if 'systems' in system:
            systems = pricing.search([('type', '=', 'systems'), ('allow_other_customer', '=', True)], limit=1).product_id
        if 'field_400_hz' in system:
            field_400_hz = pricing.search([('type', '=', '400hz'), ('allow_other_customer', '=', True)], limit=1).product_id
        if 'ground_handling' in system:
            ground_handling = pricing.search([('type', '=', 'ground_handling'), ('allow_other_customer', '=', True)], limit=1).product_id
        if 'aircraft_parking_not_registered' in system:
            aircraft_parking_not_registered = pricing.search([('type', '=', 'aircraft_parking_not_registered'), ('allow_other_customer', '=', True)], limit=1).product_id
        if 'aircraft_registered' in system:
            aircraft_registered = pricing.search([('type', '=', 'aircraft_registered'), ('allow_other_customer', '=', True)], limit=1).product_id
        if 'plb_busses' in system:
            plb_busses = pricing.search([('type', '=', 'PLBs_busses'), ('allow_other_customer', '=', True)], limit=1).product_id
        if 'security_services' in system:
            security_services = pricing.search([('type', '=', 'security_services'), ('allow_other_customer', '=', True)], limit=1).product_id
        if 'bus_transportation' in system:
            bus_transportation = pricing.search([('type', '=', 'bus_transportation'), ('allow_other_customer', '=', True)], limit=1).product_id

        # Search for the income account
        if term_facilities_utilization:
            if term_facilities_utilization.property_account_income_id:
                term_facilities_utilization_account = term_facilities_utilization.property_account_income_id.id
            elif term_facilities_utilization.categ_id.property_account_income_categ_id:
                term_facilities_utilization_account = term_facilities_utilization.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                % (term_facilities_utilization.name, term_facilities_utilization.id))

        if systems:
            # Search for the income account
            if systems.property_account_income_id:
                systems_account = systems.property_account_income_id.id
            elif systems.categ_id.property_account_income_categ_id:
                systems_account = systems.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                % (systems.name, systems.id))
        if field_400_hz:
            if field_400_hz.property_account_income_id:
                field_400_hz_incom_account = field_400_hz.property_account_income_id.id
            elif systems.categ_id.property_account_income_categ_id:
                field_400_hz_incom_account = field_400_hz.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income '
                                  'account for this Service: "%s" (id:%d).')
                                % (field_400_hz.name, field_400_hz.id))
        if ground_handling:
            if ground_handling.property_account_income_id:
                ground_handling_account = ground_handling.property_account_income_id.id
            elif ground_handling.categ_id.property_account_income_categ_id:
                ground_handling_account = ground_handling.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                % (ground_handling.name, ground_handling.id))
        if aircraft_parking_not_registered:
            if aircraft_parking_not_registered.property_account_income_id:
                aircraft_parking_not_registered_account = aircraft_parking_not_registered.property_account_income_id.id
            elif aircraft_parking_not_registered.categ_id.property_account_income_categ_id:
                aircraft_parking_not_registered_account = aircraft_parking_not_registered.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                % (aircraft_parking_not_registered.name, aircraft_parking_not_registered.id))
        if aircraft_registered:
            if aircraft_registered.property_account_income_id:
                aircraft_registered_account = aircraft_registered.property_account_income_id.id
            elif aircraft_registered.categ_id.property_account_income_categ_id:
                aircraft_registered_account = aircraft_registered.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                % (aircraft_registered.name, aircraft_registered.id))
        if plb_busses:
            if plb_busses.property_account_income_id:
                plb_busses_account = plb_busses.property_account_income_id.id
            elif plb_busses.categ_id.property_account_income_categ_id:
                plb_busses_account = plb_busses.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                % (plb_busses.name, plb_busses.id))
        if security_services:
            if security_services.property_account_income_id:
                security_services_account = security_services.property_account_income_id.id
            elif security_services.categ_id.property_account_income_categ_id:
                security_services_account = security_services.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                % (security_services.name, security_services.id))

        if bus_transportation:
            if bus_transportation.property_account_income_id:
                bus_transportation_account = bus_transportation.property_account_income_id.id
            elif bus_transportation.categ_id.property_account_income_categ_id:
                bus_transportation_account = bus_transportation.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                % (bus_transportation.name, bus_transportation.id))

        invoice_appendix_perv = self.env['invoice.appendix'].search([('from_date', '=', self.from_date), ('to_date', '=', self.to_date), ('partner_id', '=', self.partner_id.id)])
        invoice_appendix_pervious = None
        if invoice_appendix_perv:
            for rec in invoice_appendix_perv:
                if rec != self:
                    invoice_appendix_pervious = rec

        if invoice_appendix_pervious:
            bus_transporatation_price = term_facilities_price = systems_price = field_400_hz_price = ground_handling_price = aircraft_parking_not_registered_price = aircraft_registered_price = plb_busses_price = security_services_price = 0.0
            if term_facilities_utilization:
                term_facilities_price = sum(self.invoice_appendix_line_ids.mapped('term_facilities_utilization'))
            if systems:
                systems_price = sum(self.invoice_appendix_line_ids.mapped('systems'))
            if field_400_hz:
                field_400_hz_price = sum(self.invoice_appendix_line_ids.mapped('field_400_hz'))
            if ground_handling:
                ground_handling_price = sum(self.invoice_appendix_line_ids.mapped('ground_handling'))
            if aircraft_parking_not_registered:
                aircraft_parking_not_registered_price = sum(
                    self.invoice_appendix_line_ids.mapped('aircraft_parking_not_registered'))
            if aircraft_registered:
                aircraft_registered_price = sum(self.invoice_appendix_line_ids.mapped('aircraft_registered'))
            if plb_busses:
                plb_busses_price = sum(self.invoice_appendix_line_ids.mapped('plb_busses'))
            if security_services:
                security_services_price = sum(self.invoice_appendix_line_ids.mapped('security_services'))
            if bus_transportation:
                bus_transporatation_price = sum(self.invoice_appendix_line_ids.mapped('bus_transportation'))
            current_total = term_facilities_price + systems_price + field_400_hz_price + ground_handling_price + aircraft_parking_not_registered_price
            current_total += bus_transporatation_price + aircraft_registered_price + plb_busses_price + security_services_price

            # ///////////////////// Prev total //////////////////////////

            term_facilities_price_prev = systems_price_prev = field_400_hz_price_prev = ground_handling_price_prev = aircraft_parking_not_registered_price_prev = 0.0
            aircraft_registered_price_prev = plb_busses_price_prev = security_services_price_prev = bus_transportation_prev = 0.0
            if term_facilities_utilization:
                term_facilities_price_prev = sum(invoice_appendix_pervious.invoice_appendix_line_ids.mapped(
                    'term_facilities_utilization'))
            if systems:
                systems_price_prev = sum(
                    invoice_appendix_pervious.invoice_appendix_line_ids.mapped('systems'))
            if field_400_hz:
                field_400_hz_price_prev = sum(
                    invoice_appendix_pervious.invoice_appendix_line_ids.mapped('field_400_hz'))
            if ground_handling:
                ground_handling_price_prev = sum(
                    invoice_appendix_pervious.invoice_appendix_line_ids.mapped('ground_handling'))
            if aircraft_parking_not_registered:
                aircraft_parking_not_registered_price_prev = sum(
                    invoice_appendix_pervious.invoice_appendix_line_ids.mapped(
                        'aircraft_parking_not_registered'))
            if aircraft_registered:
                aircraft_registered_price_prev = sum(
                    invoice_appendix_pervious.invoice_appendix_line_ids.mapped('aircraft_registered'))
            if plb_busses:
                plb_busses_price_prev = sum(
                    invoice_appendix_pervious.invoice_appendix_line_ids.mapped('plb_busses'))
            if security_services:
                security_services_price_prev = sum(
                    invoice_appendix_pervious.invoice_appendix_line_ids.mapped('security_services'))
            if bus_transportation:
                bus_transportation_prev = sum(invoice_appendix_pervious.invoice_appendix_line_ids.mapped('bus_transportation'))
            prev_total = term_facilities_price_prev + systems_price_prev + field_400_hz_price_prev + ground_handling_price_prev
            prev_total += aircraft_parking_not_registered_price_prev + aircraft_registered_price_prev + plb_busses_price_prev + security_services_price_prev
            prev_total += bus_transportation_prev

            # //////////////////////////////////// difference ////////////////////////////////////////
            diff = current_total - prev_total
            if diff < 0:
                invoice_lines = []
                product_diff_credit_note = self.env['product.product'].search([('is_credit_note', '=', True)], limit=1)
                # Search for the income account
                if product_diff_credit_note.property_account_income_id:
                    product_diff_credit_note_account = product_diff_credit_note.property_account_income_id.id
                elif product_diff_credit_note.categ_id.property_account_income_categ_id:
                    product_diff_credit_note_account = product_diff_credit_note.categ_id.property_account_income_categ_id.id
                else:
                    raise UserError(_('Please define income '
                                      'account for this Service: "%s" (id:%d).')
                                    % (product_diff_credit_note.name, product_diff_credit_note.id))

                invoice_lines.append((0, 0, {
                    'name': str(product_diff_credit_note.name) + ' - ' + str('Credit note from appendix'),
                    'product_id': product_diff_credit_note.id,
                    'tax_ids': product_diff_credit_note.taxes_id.ids,
                    'account_id': product_diff_credit_note_account,
                    'price_unit': abs(diff)
                }))

                vals = {
                    'appendix_id': self.id,
                    'appendix_another_customer': True,
                    'move_type': 'out_refund',
                    'invoice_date': self.from_date,
                    'invoice_date_due': self.from_date,
                    'date': self.from_date,
                    'invoice_origin': self.name,
                    'customer_contact_id': self.partner_id.child_ids[0] if self.partner_id.child_ids else False,
                    'partner_id': self.partner_id.id,
                    'invoice_user_id': self.env.user.id,
                    'invoice_line_ids': invoice_lines,
                }
                # Invoice Creating
                account_inv_obj.create(vals)
            else:
                related_previouse_invoice = self.env['account.move'].search(
                    [('appendix_id', '=', invoice_appendix_pervious.id), ('appendix_another_customer', '=', True)], limit=1)
                related_previouse_invoice.button_cancel()
                invoice_lines = []
                if term_facilities_utilization:
                    term_facilities_price = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped(
                            'term_facilities_utilization'))
                    if term_facilities_price > 0:
                        invoice_lines.append((0, 0, {
                            'name': term_facilities_utilization.name + str(' With Tax'),
                            'product_id': term_facilities_utilization.id,
                            'tax_ids': term_facilities_utilization.taxes_id.ids,
                            'account_id': term_facilities_utilization_account,
                            'price_unit': term_facilities_price
                        }))
                    term_facilities_price_without_vat = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped(
                            'term_facilities_utilization'))
                    if term_facilities_price_without_vat > 0:
                        invoice_lines.append((0, 0, {
                            'name': term_facilities_utilization.name,
                            'product_id': term_facilities_utilization.id,
                            'account_id': term_facilities_utilization_account,
                            'price_unit': term_facilities_price_without_vat
                        }))
                if systems:

                    systems_price = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('systems'))
                    if systems_price > 0:
                        invoice_lines.append((0, 0, {
                            'name': systems.name + str(' With Tax'),
                            'product_id': systems.id,
                            'tax_ids': systems.taxes_id.ids,
                            'account_id': systems_account,
                            'price_unit': systems_price
                        }))
                    systems_price_without_vat = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('systems'))
                    if systems_price_without_vat > 0:
                        invoice_lines.append((0, 0, {
                            'name': systems.name,
                            'product_id': systems.id,
                            'account_id': systems_account,
                            'price_unit': systems_price_without_vat
                        }))

                if field_400_hz:

                    field_400_hz_price = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('field_400_hz'))
                    if field_400_hz_price > 0:
                        invoice_lines.append((0, 0, {
                            'name': field_400_hz.name + str(' With Tax'),
                            'product_id': field_400_hz.id,
                            'tax_ids': field_400_hz.taxes_id.ids,
                            'account_id': field_400_hz_incom_account,
                            'price_unit': field_400_hz_price
                        }))
                    field_400_hz_price_without_vat = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('field_400_hz'))
                    if field_400_hz_price_without_vat > 0:
                        invoice_lines.append((0, 0, {
                            'name': field_400_hz.name,
                            'product_id': field_400_hz.id,
                            'account_id': field_400_hz_incom_account,
                            'price_unit': field_400_hz_price_without_vat
                        }))
                if ground_handling:

                    ground_handling_price = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('ground_handling'))
                    if ground_handling_price > 0:
                        invoice_lines.append((0, 0, {
                            'name': ground_handling.name + str(' With Tax'),
                            'product_id': ground_handling.id,
                            'tax_ids': ground_handling.taxes_id.ids,
                            'account_id': ground_handling_account,
                            'price_unit': ground_handling_price
                        }))
                    ground_handling_price_without_tax = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('ground_handling'))
                    if ground_handling_price_without_tax > 0:
                        invoice_lines.append((0, 0, {
                            'name': ground_handling.name,
                            'product_id': ground_handling.id,
                            'account_id': ground_handling_account,
                            'price_unit': ground_handling_price_without_tax
                        }))

                if aircraft_parking_not_registered:
                    aircraft_parking_not_registered_price = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped(
                            'aircraft_parking_not_registered'))
                    if aircraft_parking_not_registered_price > 0:
                        invoice_lines.append((0, 0, {
                            'name': aircraft_parking_not_registered.name + str(' With Tax'),
                            'product_id': aircraft_parking_not_registered.id,
                            'tax_ids': aircraft_parking_not_registered.taxes_id.ids,
                            'account_id': aircraft_parking_not_registered_account,
                            'price_unit': aircraft_parking_not_registered_price
                        }))
                    aircraft_parking_not_registered_price_without_tax = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped(
                            'aircraft_parking_not_registered'))
                    if aircraft_parking_not_registered_price_without_tax > 0:
                        invoice_lines.append((0, 0, {
                            'name': aircraft_parking_not_registered.name,
                            'product_id': aircraft_parking_not_registered.id,
                            'account_id': aircraft_parking_not_registered_account,
                            'price_unit': aircraft_parking_not_registered_price_without_tax
                        }))

                if aircraft_registered:

                    aircraft_registered_price = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped(
                            'aircraft_registered'))
                    if aircraft_registered_price > 0:
                        invoice_lines.append((0, 0, {
                            'name': aircraft_registered.name + str(' With Tax'),
                            'product_id': aircraft_registered.id,
                            'tax_ids': aircraft_registered.taxes_id.ids,
                            'account_id': aircraft_registered_account,
                            'price_unit': aircraft_registered_price
                        }))
                    aircraft_registered_price_without_tax = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped(
                            'aircraft_registered'))
                    if aircraft_registered_price_without_tax > 0:
                        invoice_lines.append((0, 0, {
                            'name': aircraft_registered.name,
                            'product_id': aircraft_registered.id,
                            'account_id': aircraft_registered_account,
                            'price_unit': aircraft_registered_price_without_tax
                        }))

                if plb_busses:

                    plb_busses_price = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('plb_busses'))
                    if plb_busses_price > 0:
                        invoice_lines.append((0, 0, {
                            'name': plb_busses.name + str(' With Tax'),
                            'product_id': plb_busses.id,
                            'tax_ids': plb_busses.taxes_id.ids,
                            'account_id': plb_busses_account,
                            'price_unit': plb_busses_price
                        }))
                    plb_busses_price_without_tax = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('plb_busses'))
                    if plb_busses_price_without_tax > 0:
                        invoice_lines.append((0, 0, {
                            'name': plb_busses.name,
                            'product_id': plb_busses.id,
                            'account_id': plb_busses_account,
                            'price_unit': plb_busses_price_without_tax
                        }))
                if security_services:

                    security_services_price = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped(
                            'security_services'))
                    if security_services_price > 0:
                        invoice_lines.append((0, 0, {
                            'name': security_services.name + str(' With Tax'),
                            'product_id': security_services.id,
                            'tax_ids': security_services.taxes_id.ids,
                            'account_id': security_services_account,
                            'price_unit': security_services_price
                        }))
                    security_services_price_without_tax = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped(
                            'security_services'))
                    if security_services_price_without_tax > 0:
                        invoice_lines.append((0, 0, {
                            'name': security_services.name,
                            'product_id': security_services.id,
                            'tax_ids': security_services.taxes_id.ids,
                            'account_id': security_services_account,
                            'price_unit': security_services_price_without_tax
                        }))

                if bus_transportation:

                    bus_transportation_price = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped(
                            'bus_transportation'))
                    if bus_transportation_price > 0:
                        invoice_lines.append((0, 0, {
                            'name': bus_transportation.name + str(' With Tax'),
                            'product_id': bus_transportation.id,
                            'tax_ids': bus_transportation.taxes_id.ids,
                            'account_id': bus_transportation_account,
                            'price_unit': bus_transportation_price
                        }))
                    bus_transportation_price_without_tax = sum(
                        self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped(
                            'bus_transportation'))
                    if bus_transportation_price_without_tax > 0:
                        invoice_lines.append((0, 0, {
                            'name': bus_transportation.name,
                            'product_id': bus_transportation.id,
                            'tax_ids': bus_transportation.taxes_id.ids,
                            'account_id': bus_transportation_account,
                            'price_unit': bus_transportation_price_without_tax
                        }))

                vals = {
                    'appendix_id': self.id,
                    'appendix_another_customer': True,
                    'move_type': 'out_invoice',
                    'invoice_date': self.from_date,
                    'invoice_date_due': self.from_date,
                    'date': self.from_date,
                    'invoice_origin': self.name,
                    'customer_contact_id': self.partner_id.child_ids[0] if self.partner_id.child_ids else False,
                    'partner_id': self.partner_id.id,
                    'invoice_user_id': self.env.user.id,
                    'invoice_line_ids': invoice_lines,
                }
                # invoice creating
                vals.update({'partner_id': partner_id.id, 'customer_contact_id': partner_id.child_ids[0] if partner_id.child_ids else False})
                account_inv_obj.create(vals)

        else:
            invoice_lines = []
            if term_facilities_utilization:
                term_facilities_price = sum(self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped(
                    'term_facilities_utilization'))
                if term_facilities_price > 0:
                    invoice_lines.append((0, 0, {
                        'name': term_facilities_utilization.name + str(' With Tax'),
                        'product_id': term_facilities_utilization.id,
                        'tax_ids': term_facilities_utilization.taxes_id.ids,
                        'account_id': term_facilities_utilization_account,
                        'price_unit': term_facilities_price
                    }))
                term_facilities_price_without_vat = sum(
                    self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped(
                        'term_facilities_utilization'))
                if term_facilities_price_without_vat > 0:
                    invoice_lines.append((0, 0, {
                        'name': term_facilities_utilization.name,
                        'product_id': term_facilities_utilization.id,
                        'account_id': term_facilities_utilization_account,
                        'price_unit': term_facilities_price_without_vat
                    }))
            if systems:
                systems_price = sum(
                    self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('systems'))
                if systems_price > 0:
                    invoice_lines.append((0, 0, {
                        'name': systems.name + str(' With Tax'),
                        'product_id': systems.id,
                        'tax_ids': systems.taxes_id.ids,
                        'account_id': systems_account,
                        'price_unit': systems_price
                    }))
                systems_price_without_vat = sum(
                    self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('systems'))
                if systems_price_without_vat > 0:
                    invoice_lines.append((0, 0, {
                        'name': systems.name,
                        'product_id': systems.id,
                        'account_id': systems_account,
                        'price_unit': systems_price_without_vat
                    }))

            if field_400_hz:

                field_400_hz_price = sum(
                    self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('field_400_hz'))
                if field_400_hz_price > 0:
                    invoice_lines.append((0, 0, {
                        'name': field_400_hz.name + str(' With Tax'),
                        'product_id': field_400_hz.id,
                        'tax_ids': field_400_hz.taxes_id.ids,
                        'account_id': field_400_hz_incom_account,
                        'price_unit': field_400_hz_price
                    }))
                field_400_hz_price_without_vat = sum(
                    self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('field_400_hz'))
                if field_400_hz_price_without_vat > 0:
                    invoice_lines.append((0, 0, {
                        'name': field_400_hz.name,
                        'product_id': field_400_hz.id,
                        'account_id': field_400_hz_incom_account,
                        'price_unit': field_400_hz_price_without_vat
                    }))
            if ground_handling:
                ground_handling_price = sum(
                    self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('ground_handling'))
                if ground_handling_price > 0:
                    invoice_lines.append((0, 0, {
                        'name': ground_handling.name + str(' With Tax'),
                        'product_id': ground_handling.id,
                        'tax_ids': ground_handling.taxes_id.ids,
                        'account_id': ground_handling_account,
                        'price_unit': ground_handling_price
                    }))
                ground_handling_price_without_tax = sum(
                    self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('ground_handling'))
                if ground_handling_price_without_tax > 0:
                    invoice_lines.append((0, 0, {
                        'name': ground_handling.name,
                        'product_id': ground_handling.id,
                        'account_id': ground_handling_account,
                        'price_unit': ground_handling_price_without_tax
                    }))

            if aircraft_parking_not_registered:

                aircraft_parking_not_registered_price = sum(
                    self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped(
                        'aircraft_parking_not_registered'))
                if aircraft_parking_not_registered_price > 0:
                    invoice_lines.append((0, 0, {
                        'name': aircraft_parking_not_registered.name + str(' With Tax'),
                        'product_id': aircraft_parking_not_registered.id,
                        'tax_ids': aircraft_parking_not_registered.taxes_id.ids,
                        'account_id': aircraft_parking_not_registered_account,
                        'price_unit': aircraft_parking_not_registered_price
                    }))
                aircraft_parking_not_registered_price_without_tax = sum(
                    self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped(
                        'aircraft_parking_not_registered'))
                if aircraft_parking_not_registered_price_without_tax > 0:
                    invoice_lines.append((0, 0, {
                        'name': aircraft_parking_not_registered.name,
                        'product_id': aircraft_parking_not_registered.id,
                        'account_id': aircraft_parking_not_registered_account,
                        'price_unit': aircraft_parking_not_registered_price_without_tax
                    }))

            if aircraft_registered:

                aircraft_registered_price = sum(
                    self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('aircraft_registered'))
                if aircraft_registered_price > 0:
                    invoice_lines.append((0, 0, {
                        'name': aircraft_registered.name + str(' With Tax'),
                        'product_id': aircraft_registered.id,
                        'tax_ids': aircraft_registered.taxes_id.ids,
                        'account_id': aircraft_registered_account,
                        'price_unit': aircraft_registered_price
                    }))
                aircraft_registered_price_without_tax = sum(
                    self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('aircraft_registered'))
                if aircraft_registered_price_without_tax > 0:
                    invoice_lines.append((0, 0, {
                        'name': aircraft_registered.name,
                        'product_id': aircraft_registered.id,
                        'account_id': aircraft_registered_account,
                        'price_unit': aircraft_registered_price_without_tax
                    }))

            if plb_busses:

                plb_busses_price = sum(
                    self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('plb_busses'))
                if plb_busses_price > 0:
                    invoice_lines.append((0, 0, {
                        'name': plb_busses.name + str(' With Tax'),
                        'product_id': plb_busses.id,
                        'tax_ids': plb_busses.taxes_id.ids,
                        'account_id': plb_busses_account,
                        'price_unit': plb_busses_price
                    }))
                plb_busses_price_without_tax = sum(
                    self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('plb_busses'))
                if plb_busses_price_without_tax > 0:
                    invoice_lines.append((0, 0, {
                        'name': plb_busses.name,
                        'product_id': plb_busses.id,
                        'account_id': plb_busses_account,
                        'price_unit': plb_busses_price_without_tax
                    }))
            if security_services:

                security_services_price = sum(
                    self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('security_services'))
                if security_services_price > 0:
                    invoice_lines.append((0, 0, {
                        'name': security_services.name + str(' With Tax'),
                        'product_id': security_services.id,
                        'tax_ids': security_services.taxes_id.ids,
                        'account_id': security_services_account,
                        'price_unit': security_services_price
                    }))
                security_services_price_without_tax = sum(
                    self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('security_services'))
                if security_services_price_without_tax > 0:
                    invoice_lines.append((0, 0, {
                        'name': security_services.name,
                        'product_id': security_services.id,
                        'tax_ids': security_services.taxes_id.ids,
                        'account_id': security_services_account,
                        'price_unit': security_services_price_without_tax
                    }))
            if bus_transportation:
                bus_transportation_price = sum(self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('bus_transportation'))
                if bus_transportation_price > 0:
                    invoice_lines.append((0, 0, {
                        'name': bus_transportation.name + str(' With Tax'),
                        'product_id': bus_transportation.id,
                        'tax_ids': bus_transportation.taxes_id.ids,
                        'account_id': bus_transportation_account,
                        'price_unit': bus_transportation_price

                        }))
                bus_transportation_price_without_tax = sum(
                    self.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('bus_transportation'))
                if bus_transportation_price_without_tax > 0:
                    invoice_lines.append((0, 0, {
                        'name': bus_transportation.name,
                        'product_id': bus_transportation.id,
                        'tax_ids': bus_transportation.taxes_id.ids,
                        'account_id': bus_transportation_account,
                        'price_unit': bus_transportation_price_without_tax
                    }))

            vals = {
                'appendix_id': self.id,
                'appendix_another_customer': True,
                'move_type': 'out_invoice',
                'invoice_date': self.from_date,
                'invoice_date_due': self.from_date,
                'date': self.from_date,
                'invoice_origin': self.name,
                'invoice_user_id': self.env.user.id,
                'invoice_line_ids': invoice_lines,
            }
            vals.update({'partner_id': partner_id.id, 'customer_contact_id': partner_id.child_ids[0] if partner_id.child_ids else False})

            # invoice ctrating
            account_inv_obj.create(vals)


class InvoiceAppendixLines(models.Model):
    _name = 'invoice.appendix.line'

    invoice_appendix_id = fields.Many2one("invoice.appendix", string="")
    airline_partner_id = fields.Many2one(string="Airlines", related='invoice_appendix_id.partner_id', store=True)
    # GET ALL THESE FIELDS FROM AMS DATA ACCORDING TO PARTNER

    ams_id = fields.Integer(string="ID")
    serial_number = fields.Char('Serial No')
    actual_a_time = fields.Datetime('Flight Arrival date')
    actual_d_time = fields.Datetime('Flight Departure date')
    actual_a_time_gmt = fields.Char('Flight Arrival date (GMT Time)')
    actual_d_time_gmt = fields.Char('Flight Departure date (GMT Time)')
    mode = fields.Selection(string="Mode", selection=[('a', 'A'), ('d', 'D')])  # FIXME lll
    apron = fields.Char('APRON')
    parking_stand = fields.Char('Parking Stand')  # FIXME ggggg
    aircraft_registration = fields.Char('Actual Registration')  # FIXME kkkk ٌregistration nor
    actual_aircraft = fields.Char('Aircraft Type')
    actual_category = fields.Char('Aircraft Category')
    amtow = fields.Float('AMTOW')
    airline = fields.Char('Airline Code')
    agha = fields.Char('Handling Agent')
    flight_no = fields.Char('Flight NO:')  # FIXME lkkkk
    flight_type = fields.Char('Flight Type')  # FIXME kkk
    pax = fields.Integer(string="PAX")  # FIXME lll
    terminal = fields.Char(string="Terminal")  # FIXME
    counter = fields.Char('Counter')  # FIXME
    ground_time = fields.Float(string="Ground Time")
    FLT_type = fields.Char('FLT Type')

    # SERVICES COMPUTATION FROM BILLING PRICING

    term_facilities_utilization = fields.Float(string="Terminal Facilities Utilization", compute='get_services', store=True)
    systems = fields.Float(string="systems", compute='get_services', store=True)
    field_400_hz = fields.Float(string="400hz", compute='get_services', store=True)
    ground_handling = fields.Float(string="Ground Handling",  compute='get_services', store=True)
    aircraft_parking_not_registered = fields.Float(string="Aircraft Parking Not Registered",  compute='get_services', store=True)
    aircraft_registered = fields.Float(string="Aircraft Registered ", compute='get_services', store=True)
    plb_busses = fields.Float(string="PBB Fees", compute='get_services', store=True)
    security_services = fields.Float(string="Security Charge", compute='get_services', store=True)
    bus_transportation = fields.Float(string="Buss Transportation", compute="get_services", store=True)
    fees_total = fields.Float(string="Total", compute='get_services', store=True)
    last_updated_date = fields.Datetime('Last update')
    buss_pbb = fields.Char('Buses/PBB')
    arrival_airline_to = fields.Char('Arrival Airport')
    departure_airline_from = fields.Char('Departure Airport')

    @api.depends('ams_id', 'actual_a_time', 'actual_d_time', 'mode', 'apron', 'parking_stand', 'aircraft_registration', 'actual_aircraft', 'actual_category',
                 'amtow', 'airline', 'agha', 'flight_no', 'flight_type', 'pax', 'terminal', 'counter', 'ground_time', 'invoice_appendix_id.billing_pricing_ids' )
    def get_services(self):
        for rec in self:
            rec.term_facilities_utilization = 0.0
            rec.systems = 0.0
            rec.field_400_hz = 0.0
            rec.ground_handling = 0.0
            rec.aircraft_parking_not_registered = 0.0
            rec.aircraft_registered = 0.0
            rec.plb_busses = 0.0
            rec.security_services = 0.0
            rec.bus_transportation = 0.0
            rec.fees_total = 0.0
        self._compute_dynamic_pricing()

    def _compute_dynamic_pricing(self):
        field_vals = {}
        dynamic_line_field_ids = self.env['billing.pricing'].with_context(active_test=False).search([]).mapped(
            'appendix_line_value_field')
        for field_name in dynamic_line_field_ids.mapped('name'):
            field_vals[field_name] = 0.0
        for line in self:
            line.update(line._map_dynamic_billing_pricing(field_vals))

    def _map_dynamic_billing_pricing(self, default_fields):
        self.ensure_one()
        pricing_field_values = {}
        for pricing in self.invoice_appendix_id.mapped('billing_pricing_ids'):
            if not pricing.appendix_line_value_field:
                continue
            if pricing.type == 'term_facilities_utilization':
                term_facilities_utilization = 0
                if self.mode == 'a':
                    for term in pricing.term_facilities_ids:
                        term_facilities_utilization = float(term.arrival_passenger_number) * float(self.pax)
                elif self.mode == 'd':
                    for term in pricing.term_facilities_ids:
                        term_facilities_utilization = float(term.departure_passenger_number) * float(self.pax)
                self.term_facilities_utilization = term_facilities_utilization
                pricing_field_values.update({pricing.appendix_line_value_field.name: term_facilities_utilization})
            if pricing.type == 'systems':
                systems = 0
                if self.mode == 'a':
                    for sys in pricing.system_ids:
                        systems = float(sys.arrival_passenger_number) * float(self.pax)
                elif self.mode == 'd':
                    for sys in pricing.system_ids:
                        systems = float(sys.departure_passenger_number) * float(self.pax)
                self.systems = systems
                pricing_field_values.update({pricing.appendix_line_value_field.name: systems})
            if pricing.type == '400hz':
                field_400_hz = 0
                for hz in pricing.hz_ids:
                    if hz.aircraft_category_id.name == str(self.actual_category):
                        field_400_hz = float(hz.amount)
                self.field_400_hz = field_400_hz
                pricing_field_values.update({pricing.appendix_line_value_field.name: field_400_hz})
            if pricing.type == 'ground_handling':
                ground_handling = 0
                for gh in pricing.ground_handling_ids:
                    if gh.aircraft_category_id.name == str(self.actual_category):
                        ground_handling = float(gh.amount)
                self.ground_handling = ground_handling
                pricing_field_values.update({pricing.appendix_line_value_field.name: ground_handling})
            if pricing.type == 'aircraft_parking_not_registered':
                aircraft_parking_not_registered = 0
                if self.aircraft_registration and self.apron == 'APRON6' and self.mode == 'd':
                    if str(self.aircraft_registration[:2]) != 'HZ' and float(self.amtow) > .5:

                        for not_reg in pricing.aircraft_not_registered_ids:
                            if not_reg.from_time < self.ground_time <= not_reg.to_time and not not_reg.is_above:
                                aircraft_parking_not_registered = not_reg.price

                            if not_reg.from_time < self.ground_time and not_reg.is_above:
                                max_time = max(pricing.aircraft_not_registered_ids.mapped('to_time'))
                                max_time_price = pricing.aircraft_not_registered_ids.filtered(lambda x: x.to_time == max_time)
                                above_from = self.ground_time - not_reg.from_time  # 3:29
                                if max_time != 0:
                                    all_above = above_from / max_time
                                    all_above_int = int(all_above)
                                    all_above_float = float(all_above) - all_above_int
                                    if all_above_float > 0:
                                        all_above_float = 1
                                    else:
                                        all_above_float = 0
                                    all_above_total = all_above_int + all_above_float
                                    aircraft_parking_not_registered = (max_time_price.price + (all_above_total * not_reg.price)) * self.amtow
                self.aircraft_parking_not_registered = aircraft_parking_not_registered
                pricing_field_values.update({pricing.appendix_line_value_field.name: aircraft_parking_not_registered})
            if pricing.type == 'aircraft_registered':
                aircraft_registered = 0
                if self.aircraft_registration and self.apron == 'APRON6' and self.mode == 'd':
                    if str(self.aircraft_registration[:2]) == 'HZ' and self.amtow > .5:
                        for reg in pricing.aircraft_registered_ids:
                            if reg.from_time < self.ground_time <= reg.to_time and not reg.is_above:
                                aircraft_registered = reg.price
                            if reg.from_time < self.ground_time and reg.is_above:
                                max_time = max(
                                    pricing.aircraft_registered_ids.mapped('to_time'))
                                max_time_price = pricing.aircraft_registered_ids.filtered(lambda x: x.to_time == max_time)
                                above_from = self.ground_time - reg.from_time
                                if max_time != 0:
                                    all_above = above_from / max_time
                                    all_above_int = int(all_above)
                                    all_above_float = float(all_above) - all_above_int
                                    if all_above_float > 0:
                                        all_above_float = 1
                                    else:
                                        all_above_float = 0
                                    all_above_total = all_above_int + all_above_float
                                    aircraft_registered = (max_time_price.price + (all_above_total * reg.price)) * self.amtow
                self.aircraft_registered = aircraft_registered
                pricing_field_values.update({pricing.appendix_line_value_field.name: aircraft_registered})
            if pricing.type == 'PLBs_busses':
                plb_busses = 0
                if self.parking_stand in ['6-%s' % a for a in range(1,11)]:
                    for ppb in pricing.blp_buses_ids:
                        if ppb.from_ton < float(self.amtow) <= ppb.to_ton and not ppb.is_above:
                            plb_busses = float(ppb.price)
                        if ppb.from_ton < float(self.amtow) and ppb.is_above:
                            plb_busses = float(ppb.price)
                self.plb_busses = plb_busses
                pricing_field_values.update({pricing.appendix_line_value_field.name: plb_busses})
            if pricing.type == 'security_services':
                security_services = 0
                if self.mode == 'd':
                    for sec in pricing.security_services_ids:
                        if sec.from_ton < float(self.amtow) <= sec.to_ton and not sec.is_above:
                            security_services = float(sec.price)
                        if sec.from_ton < float(self.amtow) and sec.is_above:
                            security_services = float(sec.price)
                self.security_services = security_services
                pricing_field_values.update({pricing.appendix_line_value_field.name: security_services})
            if pricing.type == 'bus_transportation':
                bus_transportation = 0
                for buss in pricing.buss_transportation_ids:
                    bus_transportation = float(buss.subtotal)
                self.bus_transportation = bus_transportation
                pricing_field_values.update({pricing.appendix_line_value_field.name: bus_transportation})

        fees_total = sum(pricing_field_values.values())
        pricing_field_values.update(fees_total=fees_total)
        return {
            **default_fields, **pricing_field_values
        }


class MailInvoiceAppendix(models.Model):
    _name = 'mail.invoice_appendix'
    invoice_appendixs = fields.Many2many('invoice.appendix', string='Recipients',  default=lambda s: s.env.context.get("active_ids", []))

    def send_invoice_appendix_by_mail(self):
        for rec in self:
            for app in rec.invoice_appendixs:
                app.send_mail_appendix_and_invoice()

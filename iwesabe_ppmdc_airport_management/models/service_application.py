# -*- coding:utf-8 -*-
from odoo import _, api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import ValidationError

import time


class ServiceApplication(models.Model):
    _name = 'service.application'
    _description = 'Service Application'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'id desc'

    ARRAY_READONLY = {'confirm': [('readonly', True)]}

    name = fields.Char(string="Name", required=True, default="/")
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    date = fields.Date(string="Date", required=True, default=fields.Date.today())
    service_type = fields.Selection([('new', 'New Installation'), ('transfer', 'Transfer'), ('add_new_item', 'Add New Item'), ('disable', 'Disable')], string="Service Type", default="new")
    tenancy_id = fields.Many2one('tenant.tenancy', string='Tenancy')
    applicant = fields.Selection([('governmental', 'Govermental'), ('airlines', 'Airlines'), ('other', 'Other')], string="Applicant")
    information_data_ids = fields.One2many('tenancy.service', 'service_application_id', string="Information Data")
    telephone_service_ids = fields.One2many('service.contract.phone.extention', 'service_application_id', string="Telephone Servcie")
    equipment_ids = fields.One2many('tenancy.equipment', 'service_application_id', string="Equipments")
    # Applicant Approval
    applicant_name = fields.Char(string="Applicant Name")
    applicant_phone = fields.Char(string="Applicant Phone")
    applicant_mobile = fields.Char(string="Applicant Mobile")
    applicant_address = fields.Char(string="Applicant Address")
    applicant_job_title = fields.Char(string="Job Title")
    signature = fields.Html(string="Signature")
    # property managment approval
    property_side = fields.Selection([
          ('inside_ierminal', 'Inside Terminal'),
          ('out_terminal', 'Out Of terminal'),
          ('area_side', 'Area Side'),
          ('octagon', 'Octagon')
          ],
          string="Property Side"
     )
    office_no = fields.Char(string="Office No")
    contract_no = fields.Char(string="Contract No")
    manager_name = fields.Char(string="Manager Name")
    manager_signature = fields.Html(string="Manager Signature")
    signature_date = fields.Date(string="Signature Date")
    state = fields.Selection([
          # ('qu_draft', 'Draft'),
          ('quotations', 'Quotations'),
          ('tenancy', 'Tenancy'),
          ('sent', 'Sent'),
          ('confirm', 'Confirm'),
          ('service_application', 'Service Application'),
          ('draft', 'Draft'),
          ('done', 'Done'),
          ('cancel', 'Cancel')
          ],
          string="Status", default='draft')
    quotation = fields.Boolean(string="Quotation")
    notes = fields.Html(string="Notes")
    from_property_id = fields.Many2one('property.property', string='From Property')
    to_property_id = fields.Many2one('property.property', string='To Property')
    property_ids = fields.One2many('tenancy.property', 'service_application_id', string="Property")
    instructions = fields.Text(string="Instructions")
    customer_po_number = fields.Char(string="Customer Po Number")
    customer_po_number_attach = fields.Binary(string="Customer Po Number Attachment")
    date_end = fields.Date(string='Expiration Date', index=True, help="Tenancy contract end date.", track_visibility='onchange')
    date_end_hijri = fields.Char(string="Expiration Date Hijri", track_visibility='onchange')
    date_start = fields.Date(string='Start Date', default=lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT), help="Tenancy contract start date .", track_visibility='onchange')
    date_start_hijri = fields.Char(string="Start Date Hijri", track_visibility='onchange')
    date_order = fields.Date(string='Date', default=lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT), index=True, help="Tenancy contract creation date.", track_visibility='onchange', states=ARRAY_READONLY)
    date_order_hijri = fields.Char(string="Hijei Date", states=ARRAY_READONLY)
    annual_rate = fields.Float(string="Annual increase rate(%)", default="10", states=ARRAY_READONLY)
    rent_type_id = fields.Many2one('rent.type', string='Season Rent', states=ARRAY_READONLY)
    total_rent = fields.Monetary(string='Total Rent', store=True, readonly=True, currency_field='currency_id', compute='_compute_total_rent', help='Total rent of this Tenancy.')
    currency_id = fields.Many2one('res.currency', string='Currency')

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

    @api.depends('property_ids.total')
    def _compute_total_rent(self):
        for rec in self:
            rec.total_rent = sum(r.total for r in self.property_ids)

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

    def action_quotations(self):
        self.write({'state': 'quotations'})

    def action_confirm(self):
        self.write({'state': 'confirm'})

    def action_service_application(self):
        self.write({'state': 'service_application'})

    def action_create_tenancy(self):
        # self.write({'state': 'tenancy'})
        self.quotation = False

        context = {
              'default_tenant_id': self.partner_id.id,
              'default_date_order': fields.Date.today(),
              'default_service_application_id': self.id
          }
        return {
              'res_model': 'tenant.tenancy',
              'type': 'ir.actions.act_window',
              'view_type': 'form',
              'view_id': self.env.ref('iwesabe_ppmdc_airport_management.view_tenant_tenancy_form').id,
              'view_mode': 'form',
              'target': 'current',
              'context': context
          }

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    def action_view_tenancy(self):
        actions = self.env.ref('iwesabe_ppmdc_airport_management.action_tenancy_tenant_view').read()[0]
        actions['domain'] = [('service_application_id', '=', self.id)]
        actions['context'] = {'create': False}
        return actions

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('service.application')
        return super(ServiceApplication, self).create(vals)

    def _find_mail_template(self, force_confirmation_template=False):
        template_id = False

        template_id = int(self.env['ir.config_parameter'].sudo().get_param('iwesabe_ppmdc_airport_management.email_template_service_application'))
        template_id = self.env['mail.template'].search([('id', '=', template_id)]).id
        if not template_id:
            template_id = self.env['ir.model.data'].xmlid_to_res_id('iwesabe_ppmdc_airport_management.email_template_service_application', raise_if_not_found=False)

        return template_id

    def action_quotation_send(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        self.state = 'sent'
        template_id = self._find_mail_template()
        ctx = {
            'default_model': 'service.application',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
          }
        return {
               'type': 'ir.actions.act_window',
               'view_mode': 'form',
               'res_model': 'mail.compose.message',
               'views': [(False, 'form')],
               'view_id': False,
               'target': 'new',
               'context': ctx,
          }


class TelephoneService(models.Model):
    _name = 'telephone.service'
    _description = 'Telephone Service'
    _rec_name = 'service_id'

    service_id = fields.Many2one('telephone.service.service', string='Service')
    number = fields.Integer(string="Number", required=True, default=1)
    application_id = fields.Many2one('service.application', string='Application')


class TelephoneServiceService(models.Model):
    _name = 'telephone.service.service'
    _discription = 'Telephone Service Service'

    name = fields.Char(string="Service", required=True)


class InformationData(models.Model):
    _name = 'information.data'
    _description = 'Information Data'
    _rec_name = 'service_id'

    service_id = fields.Many2one('information.data.service', string='Service')
    number = fields.Integer(string="Number", required=True, default=1)
    application_id = fields.Many2one('service.application', string='Application')


class InformationDataService(models.Model):
    _name = 'information.data.service'
    _description = 'Information Data'

    name = fields.Char(string="Service", required=True)

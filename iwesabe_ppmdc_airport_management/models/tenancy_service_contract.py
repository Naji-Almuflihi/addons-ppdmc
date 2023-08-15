# -*- coding:utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.misc import get_lang


phone_extention_numbers = []


class TenancyServiceContract(models.Model):
    _name = 'tenancy.service.contract'
    _description = 'Tenancy Service contract'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    ARRAY_READONLY = {
        'open': [('readonly', True)],
        'pending': [('readonly', True)],
        'close': [('readonly', True)],
        'cancelled': [('readonly', True)],
    }

    name = fields.Char(string="Name", required=True, states=ARRAY_READONLY)

    partner_id = fields.Many2one('res.partner', string='Tenant', required=True, states=ARRAY_READONLY)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    tenancy_id = fields.Many2one('tenant.tenancy', string='Tenancy Contract', required=True, states=ARRAY_READONLY)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('quotation', 'Quotation'),
        ('open', 'Confirmed'),
        ('pending', 'To Renew'),
        ('close', 'Closed'),
        ('cancelled', 'Cancelled')
    ],
        string="Status", default='draft', track_visibility='onchange')
    date = fields.Date(string="Date", default=fields.Date.today(), states=ARRAY_READONLY)
    date_hijri = fields.Char(string="Date Hijri", states=ARRAY_READONLY)
    date_start = fields.Date(string="Start Date", required=True, states=ARRAY_READONLY)
    date_start_hijri = fields.Char(string="Start Date Hijri", required=True, states=ARRAY_READONLY)
    date_end = fields.Date(string="End Date", required=True, track_visibility='onchange', states=ARRAY_READONLY)
    date_end_hijri = fields.Char(string="End Date Hijri", required=True, track_visibility='onchange', states=ARRAY_READONLY)
    phone_extention_ids = fields.One2many('tenancy.phone.extention', 'service_contract_id', string="Phone Extention")
    phone_extention_count = fields.Integer(string="Phone Extention Count", compute='_compute_phone_extention_count', store=True)
    equipment_ids = fields.One2many('tenancy.equipment', 'service_contract_id', string="Equipments")
    service_count = fields.Integer(string="Service Count", compute='_compute_service_count', store=True)
    invoice_line_ids = fields.One2many('service.contract.invoice.line', 'service_contract_id', string="Invoice Line")
    invoice_ids = fields.One2many('account.move', 'service_contract_id', string="Invoice")
    invoice_count = fields.Integer(string="Invoice count", compute='_compute_invoice_count', store=True)
    service_phone_extention_ids = fields.One2many('service.contract.phone.extention', 'service_contract_id', string="Phone Externtion Numbers")
    extention_number_ids = fields.Many2many('phone.extentaion.numbers', string='Extention Number', compute='_compute_extention_number_ids', store=True)
    service_type = fields.Selection([
          ('new', 'New Installation'),
          ('transfer', 'Transfer'),
          ('add_new_item', 'Add New Item'),
          ('disable', 'Disable')
          ], string="Service Type", default="new")
    service_ids = fields.One2many('tenancy.service', 'service_contract_id', string="Service")

    is_contract_extension = fields.Boolean(string="Contract Extension")
    tenancy_extension_id = fields.Many2one('tenant.tenancy', string='Tenancy Extension')
    implementation_service_id = fields.Many2one("implementation.service.application", string="Implementation Service")
    implementation_count = fields.Integer(compute='compute_implementation_count')
    import_number = fields.Char("Import Number")

    # equiids = fields.One2many(comodel_name="", inverse_name="", string="", required=False, )

    @api.depends('state')
    def compute_implementation_count(self):
        ims_obj = self.env['implementation.service.application']
        for rec in self:
            count = 0
            implementation_service = ims_obj.search([('tenancy_contract_id', '=', rec.id)])
            count = len(implementation_service)
            # for serv in implementation_service:
            #     count+=1
            rec.implementation_count = count

    def compute_service_implementation_count(self):
        contxt = {"default_tenancy_contract_id": self.id}
        return {
            'name': _('Implementation Service Application'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'implementation.service.application',
            'domain': [('tenancy_contract_id', '=', self.id)],
            'context': contxt
        }

    def _prepare_information_data_ids(self):
        data = []
        if self.tenancy_id:
            for rec in self.tenancy_id.information_data_ids:
                data.append((0, 0, {
                    'product_id': rec.product_id.id,
                    'points': rec.points,
                    'vlan': rec.vlan,
                    'quantity': rec.quantity,
                    'rent': rec.rent,
                    'total': rec.total
                }))
            self.service_ids = data

    def _prepare_equipment_ids(self):
        data = []
        if self.tenancy_id:
            for rec in self.tenancy_id.equipment_ids:
                data.append((0, 0, {
                    'equipment_id': rec.equipment_id.id,
                    'quantity': rec.quantity,
                    'rent': rec.rent,
                    'total': rec.total
                }))
            self.equipment_ids = data

    def _prepare_telephone_service_ids(self):
        data = []
        if self.tenancy_id:
            for rec in self.tenancy_id.telephone_service_ids:
                data.append((0, 0, {
                    'equipment_id': rec.equipment_id.id,
                    'phone_extention_id': rec.phone_extention_id.id,
                    'extention_number_id': rec.extention_number_id.id,
                    'service_contract_id': rec.service_contract_id.id,
                    'quantity': rec.quantity,
                    'rent': rec.rent,
                    'total': rec.total
                }))
            self.service_phone_extention_ids = data

    def _prepare_property_ids(self):
        data = []
        if self.tenancy_id:
            for rec in self.tenancy_id.property_ids:
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

    @api.onchange('tenancy_id')
    def onchange_tenancy_id(self):
        if self.tenancy_id:
            self._prepare_information_data_ids()
            self._prepare_telephone_service_ids()
            self._prepare_equipment_ids()

    @api.onchange('name', 'is_contract_extension')
    def filter_implementation_service(self):

        lines_service = []
        if self.is_contract_extension and self.tenancy_id:
            tenancy_record = self.env['tenancy.service.contract'].search([('id', '=', self.tenancy_id.id)])
            for rec in tenancy_record:
                if rec.implementation_service_id:
                    lines_service.append(rec.implementation_service_id.id)
        return {
            'domain': {'implementation_service_id': [('id', 'in', lines_service)]}
        }

    @api.depends('phone_extention_ids.extention_number_ids')
    def _compute_extention_number_ids(self):
        vals = []
        for rec in self.phone_extention_ids:
            for line in rec.extention_number_ids:
                vals.append(line.id)
        self.extention_number_ids = [(6, 0, vals)]

    @api.onchange('date')
    def onchange_date(self):
        if self.date:
            self.with_context({'field_to': 'date_hijri', 'field_from': 'date'}).Gregorian2hijri()

    @api.onchange('date_end')
    def onchange_date_end(self):
        if self.date_end:
            self.with_context({'field_to': 'date_end_hijri', 'field_from': 'date_end'}).Gregorian2hijri()

    @api.onchange('date_start')
    def onchange_date_start(self):
        if self.date_start:
            self.with_context({'field_to': 'date_start_hijri', 'field_from': 'date_start'}).Gregorian2hijri()

    @api.constrains('date_end')
    def _check_date_end(self):
        if self.date_end and self.tenancy_id:
            if self.date_end > self.tenancy_id.date_end:
                raise ValidationError(_('Service contact end date must be less than tenancy expiration date !!'))

    @api.onchange('property_id')
    def onchange_property_id(self):
        if self.service_contract_id.tenancy_id.property_ids:
            property_ids = [r.property_id.id for r in self.service_contract_id.tenancy_id.property_ids]
            res = {}
            res['domain'] = {'property_id': [('id', 'in', property_ids)]}
            return res

    def button_start(self):
        for rec in self.service_phone_extention_ids:
            rec.extention_number_id.reserverd = True

        return self.write({'state': 'open'})

    def button_cancel_tenancy(self):
        for record in self:
            for rec in record.service_phone_extention_ids:
                rec.action_unreserved_number()

            for rec in record.equipment_ids:
                rec.action_unreserved_number()

            record.write(
                {'state': 'cancelled'})

    def button_close(self):
        for rec in self:
            for line in rec.service_phone_extention_ids:
                line.action_unreserved_number()
            rec.write({'state': 'close'})

    def button_set_to_draft(self):
        for rec in self:
            rec.write({'state': 'draft'})

    def _find_mail_template(self, force_confirmation_template=False):
        template_id = False
        template_id = self.env['ir.model.data'].xmlid_to_res_id('iwesabe_ppmdc_airport_management.email_send_to_quotation_mail', raise_if_not_found=False)
        return template_id

    def button_send_mail(self):
        self.ensure_one()
        # template_id = self._find_mail_template()
        template_id = self.env.ref('iwesabe_ppmdc_airport_management.email_send_for_creation_mail')
        model = self.env['ir.model']._get(self._name)
        # if self.lang:
        #     lang = self._render_lang([self.id])[self.id]
        #     template_id = template_id.with_context(lang=lang)
        #     model = model.with_context(lang=lang)
        ctx = {
            'default_model': 'tenancy.service.contract',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id.id,
            'default_composition_mode': 'comment',
            'force_email': True,
            'model_description': model.display_name,
        }
        # ctx = {}
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get('mark_sc_as_draft'):
            self.filtered(lambda o: o.state == 'draft').write({'state': 'quotation'})
        return super(TenancyServiceContract, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for record in self:
            record.invoice_count = len(record.invoice_ids.ids)

    @api.depends('service_ids')
    def _compute_service_count(self):
        for record in self:
            record.service_count = len(record.service_ids.ids)

    # @api.depends('phone_extention_ids')
    # def _compute_phone_extention_count(self):
    #     for record in self:
    #         record.phone_extention_count = len(record.phone_extention_ids.ids)

    def action_view_phone_extention(self):
        actions = self.env.ref('iwesabe_ppmdc_airport_management.action_tenancy_phone').read()[0]
        actions['domain'] = [('tenancy_id', '=', self.id)]
        actions['context'] = {'default_tenancy_id': self.id,
                              'default_partner_id': self.tenant_id.id}
        return actions

    def action_view_service(self):
        actions = self.env.ref('iwesabe_ppmdc_airport_management.action_tenancy_service').read()[0]
        actions['domain'] = [('tenancy_id', '=', self.id)]
        actions['context'] = {'default_tenancy_id': self.id,
                              'default_partner_id': self.tenant_id.id}
        return actions

    def compute_invoice_line(self):
        self.invoice_line_ids.unlink()
        invcoie_line = []
        for rec in self.service_ids:
            invcoie_line.append((0, 0, {
                'name': rec.product_id.name,
                'points': rec.points,
                'price': rec.total
            }))

        for rec in self.equipment_ids:
            invcoie_line.append((0, 0, {
                'name': rec.equipment_id.name,
                'price': rec.total
            }))

        for rec in self.service_phone_extention_ids:
            invcoie_line.append((0, 0, {
                'name': rec.phone_extention_id.name,
                'price': rec.total
            }))

        self.invoice_line_ids = invcoie_line

    def create_invoice(self):
        """
        Create invoice for Rent Schedule.
        @param self: The object pointer
        """
        inv_obj = self.env['account.move']
        for rec in self:
            invoice_line = []
            for line in self.invoice_line_ids:
                invoice_line.append((0, 0, line._prepare_invoice_line()))

            ref = ''
            if rec.is_contract_extension:
                ref += 'ملحق بالعقد رقم '
                if rec.tenancy_id:
                    ref += str(rec.tenancy_id.name)
                ref += 'وعقد خدمات رقم '
                if rec.implementation_service_id:
                    ref += rec.implementation_service_id.name
                # ref = 'ملحق بالعقد رقم ' + str(rec.tenancy_id and rec.tenancy_id.name or '') + 'وعقد خدمات رقم ' + rec.implementation_service_id and rec.implementation_service_id.name or ''
            else:
                ref = self.tenancy_id.name + '-' + self.name
            invoice_vals = {
                'ref': ref,
                'move_type': 'out_invoice',
                'partner_id': self.partner_id.id,
                # 'journal_id': journal.id,  # company comes from the journal
                'invoice_origin': self.name,
                'invoice_line_ids': invoice_line,
                'company_id': self.company_id.id,
                'service_contract_id': rec.id or False,


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

    def create_implementation_service_application(self):

        lines_list = []
        phone_extention = []
        product_services = []
        equipment_list = []
        phone_extentions_list = []
        phone_extentions_number_list = []

        for equip in self.equipment_ids:
            equipment_list.append(equip.equipment_id.id)

        for line in self.service_ids:
            product_services.append(line.product_id.id)
            lines_list.append((0, 0, {
                'product_id': line.product_id.id,
                'points': line.points,
                'location_id': line.location_id.id,
                'points_ref': line.points,
                'quantity': 1,
                'rent': line.rent,
                'total': line.total,
            }))
        for equip in self.service_phone_extention_ids:

            for phone_number in equip.phone_extention_id.extention_number_ids:
                phone_extentions_number_list.append(phone_number.id)

            phone_extentions_list.append(equip.phone_extention_id.id)
            phone_extention.append((0, 0, {'phone_extention_id': equip.phone_extention_id.id}))
        propert_list = []
        for propert in self.tenancy_id.property_ids:
            propert_list.append(propert.property_id.id)
        product_list = []
        for product in self.service_ids:
            product_list.append(product.product_id.id)
        model_list = []
        for mod in self.equipment_ids:
           model_list.append(mod.equipment_id.id) 
        values = {
            'date_start': self.date_start,
            'date_end': self.date_end,
            'date': self.date,
            'partner_id': self.partner_id.id,
            'tenancy_id': self.tenancy_id.id,
            'is_service_quotation': True,
            'tenancy_contract_id': self.id,
            'property_ids': propert_list,
            'product_ids': product_list,
            'model_ids': model_list,
            # 'product_services': product_services,
            # 'equipment_ids': equipment_list,
            # 'phone_extentions_ids': phone_extentions_list,
            # 'phone_extentions_number_ids': phone_extentions_number_list,
            'service_ids': lines_list,
            'telephone_service_ids': phone_extention,
        }
        implementation_service_record = self.env['implementation.service.application'].create(values)
        self.implementation_service_id = implementation_service_record.id
        # send niotification to all IT group member--------------------------
        group_id = self.env.ref('iwesabe_ppmdc_airport_management.group_property_it')
        it_group_usr_lst = group_id.users
        # notification_ids = []
        # for nft in it_group_usr_lst:
        #     data = {'res_partner_id': nft.id, 'notification_type': 'inbox'}
        #     notification_ids.append((0, 0, data))
        # notification_data = {
        #     'message_type': 'notification',
        #     'body': 'Implementation Service Application created %s' % self.implementation_service_id.name,
        #     'subject': 'Implementation Service Application Created',
        #     'models': self._name,
        #     'res_id': self.implementation_service_id.id,
        #     'partner_ids': [self.env.user.partner_id.id],
        #     'author_id': self.env.user.partner_id.id,
        #     'notification_ids': notification_ids
        # }
        template_id = self.env.ref('iwesabe_ppmdc_airport_management.email_send_for_creation_mail')
        from_email = self.env.user.company_id.email
        to_email = [usr.email for usr in it_group_usr_lst]
        for email_to in to_email:
            template_id.write({
                'email_to': email_to,
                'email_from': from_email,
            })
            template_id.send_mail(self.id, force_send=True)

        return {
            'name': _('Implementation Service Application'),
            'res_model': 'implementation.service.application',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
            'res_id': implementation_service_record.id,
        }

    def action_view_invoice(self):
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        action['domain'] = [('service_contract_id', '=', self.id)]
        action['context'] = {
            'default_service_contract_id': self.id,
            'default_move_type': 'out_invoice',
            'create': False}
        return action


class ServiceContractInvoiceLine(models.Model):
    _name = 'service.contract.invoice.line'
    _description = 'Service Contract Invoice Line'

    name = fields.Char(string="Description", required=True)
    points = fields.Float(string="Points")
    price = fields.Float(string="Price")
    service_contract_id = fields.Many2one('tenancy.service.contract', string='Tenancy')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)

    def _prepare_invoice_line(self):
        if not self.company_id.service_income_account:
            raise ValidationError(_('Please insert service income account in configuration!!'))
        points = 1
        name = ''
        if self.points > 0:
            points = self.points
            name = self.name + str(" - ")+str(points)
        else:
            name = self.name
        return {
            'name': name,
            'account_id': self.company_id.service_income_account.id,
            'price_unit': self.price,
            'quantity': 1,
        }

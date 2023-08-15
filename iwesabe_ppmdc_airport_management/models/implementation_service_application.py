from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ImplementationServiceApplication(models.Model):
    _name = 'implementation.service.application'
    _description = 'Implementation Service Application'

    @api.depends('tenancy_id')
    def get_partner_id_from_tancy(self):
        for res in self:
            if res.tenancy_id:
                sev_contry_ids = self.env['tenancy.service.contract'].search([('tenancy_id', '=', res.tenancy_id.id), ('partner_id', '=', res.partner_id.id)])
                # res.partner_id = res.tenancy_id.tenant_id.id
                return {'domain': {'tenancy_contract_id': [('id', 'in', sev_contry_ids.ids)]}}

    @api.onchange('partner_id')
    def onchange_tenancy_id(self):
        if self.partner_id:
            self.tenancy_id = False
            tenancy_ids = self.env['tenant.tenancy'].search([('tenant_id', '=', self.partner_id.id)])
            # self.partner_id = self.tenancy_id.tenant_id.id
            return {'domain': {'tenancy_id': [('id', 'in', tenancy_ids.ids)]}}

    model_ids = fields.Many2many('maintenance.model', string='Models')
    product_ids = fields.Many2many('product.template',string='Product')
    property_ids = fields.Many2many('property.property',string='Property')
    name = fields.Char(default="New")
    tenancy_id = fields.Many2one("tenant.tenancy", string="Tenancy Contract")
    partner_id = fields.Many2one("res.partner", string="Customer", compute="get_partner_id_from_tancy", store=True)
    date = fields.Date(string="Date")
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")
    is_service_quotation = fields.Boolean(string="Service Quotation")
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('implemented', 'Implemented'), ('cancelled', 'cancelled')], string="Status", default="draft")
    tenancy_contract_id = fields.Many2one("tenancy.service.contract", string="Tenancy Service Quotation")
    service_ids = fields.One2many("service.application.line", "service_application_id")
    telephone_service_ids = fields.One2many("telephone.service.application.line", "telephone_application_id")
    # locations_ids = fields.Many2many("property.property", string="Locations")
    # product_services = fields.Many2many("product.template", string="Services Products")
    # equipment_ids = fields.Many2many("maintenance.equipment", string="Equipments")
    # phone_extentions_ids = fields.Many2many("phone.extention", string="Phone Extentions")
    # phone_extentions_number_ids = fields.Many2many("phone.extentaion.numbers", string="Phone Extentions Number")
    # phone_extention_count = fields.Integer(compute='compute_phone_extention_count')
    type_of_request = fields.Selection([('new', 'New'), ('replacment', 'Replacment'), ('cancellation', 'Cancellation')], string="Type Of Request")

    related_service_application_id = fields.Many2one('implementation.service.application', string="Related service application")
    related_service_ids = fields.One2many("service.application.line.related", "related_service_application_id")
    related_telephone_service_ids = fields.One2many("telephone.service.application.line.related", "related_telephone_application_id")

    @api.onchange('type_of_request')
    def onchnage_type_of_request(self):
        if self.type_of_request:
            self.related_service_application_id = False

    @api.onchange('related_service_application_id')
    def onchang_related_service_application_id(self):
        self.related_service_ids = False
        self.related_telephone_service_ids = False
        if self.related_service_application_id:
            service_lst = []
            for res in self.related_service_application_id.service_ids:
                data = {
                    'product_id': res.product_id.id,
                    'points': res.points,
                    'points_ref': res.points_ref,
                    'product_vlan_id': res.product_vlan_id.id,
                    'quantity': res.quantity,
                    'location_id': res.location_id.id,
                    'rent': res.rent,
                    'total': res.total,
                    'authority': res.authority,
                    'note': res.note
                }
                service_lst.append((0, 0, data))
            self.related_service_ids = service_lst
            telephone_lst = []
            for rec in self.related_service_application_id.telephone_service_ids:
                data = {
                    'equipment_id': rec.equipment_id.id,
                    'extention_number_id': rec.extention_number_id.id,
                    'phone_extention_id': rec.phone_extention_id.id,
                    'location_id': rec.location_id.id,
                    'authority': rec.authority,
                    'note': rec.note,
                    'replacement_equipnment_id': rec.replacement_equipnment_id.id,
                    'type_of_replacement': rec.type_of_replacement
                }
                telephone_lst.append((0, 0, data))
            self.related_telephone_service_ids = telephone_lst

    @api.onchange('tenancy_contract_id')
    def onchang_tenancy_contract_id(self):
        self.telephone_service_ids = False
        self.service_ids = False
        if self.tenancy_contract_id:
            data_list = []
            self.service_ids = []
            for res in self.tenancy_contract_id.service_ids:
                data = {
                    'product_id': res.product_id and res.product_id.id or False,
                    'points': res.points,
                    'points_ref': res.points
                }
                if res.product_id.is_vlan:
                    vlan_id = self.env['vlan.vlan.line'].search([('product_tmpl_id', '=', res.product_id.id)], limit=1)
                    if vlan_id:
                        data.update({'product_vlan_id': vlan_id.id})
                data_list.append((0, 0, data))
            self.service_ids = data_list
            service_id_lst = []
            self.telephone_service_ids = []
            for ser in self.tenancy_contract_id.service_phone_extention_ids:
                service_id_lst.append((0, 0, {'phone_extention_id': ser.phone_extention_id and ser.phone_extention_id.id or False}))
            self.telephone_service_ids = service_id_lst

    @api.constrains('service_ids')
    def service_ids_service(self):
        total_points = 0.0
        total_ref_points = 0.0
        for line in self.service_ids:
            total_points += line.points
            total_ref_points += line.points_ref

        if total_points > total_ref_points:
            raise ValidationError(
                _('Please Available Points'))

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('implementation.service.application.seq')
        return super(ImplementationServiceApplication, self).create(vals)

    def button_set_to_draft(self):
        for rec in self:
            rec.write({'state': 'draft'})
            for res in rec.telephone_service_ids:
                if res.extention_number_id.implementation_application_number_id == rec.id:
                    res.extention_number_id.implementation_application_number_id = False

    def button_set_to_confirmed(self):
        for rec in self:
            rec.write({'state': 'confirmed'})

    def button_set_to_implemented(self):
        for rec in self:
            list_data = []
            service_contract_id = self.env['account.move'].search([('service_contract_id', '=', rec.tenancy_contract_id.id)], limit=1)

            for res in rec.telephone_service_ids:
                res.extention_number_id.implementation_application_number_id = rec.id
                if service_contract_id:
                    data = {
                        'phone_extention_id': res.phone_extention_id.id,
                        'extention_number_id': res.extention_number_id.id,
                        'location_id': res.location_id.id,
                        'move_id': service_contract_id.id
                    }
                    list_data.append((0, 0, data))
                res.equipment_id.device_activation = True
                res.equipment_id.location_id = res.location_id.id
                res.equipment_id.property_type_id = res.location_id.property_type_id.id
                res.equipment_id.main_zone_location_id = res.location_id.main_zone_location_id.id
                res.equipment_id.module_property_zone_id = res.location_id.zone_id.id
                res.phone_extention_id.extention_number_ids.tenancy_id = rec.tenancy_id.id
                res.phone_extention_id.extention_number_ids.partner_id = rec.partner_id.id
                res.phone_extention_id.extention_number_ids.partner_id = rec.partner_id.id
                res.phone_extention_id.extention_number_ids.service_contract_id = rec.tenancy_contract_id.id
                res.phone_extention_id.extention_number_ids.reserverd = True
                res.phone_extention_id.extention_number_ids.implementation_application_number_id = rec.id
            if service_contract_id:
                service_contract_id.phone_extention_ids = list_data

            rec.write({'state': 'implemented'})

    def button_set_to_cancelled(self):
        for rec in self:
            rec.write({'state': 'cancelled'})
            for res in rec.telephone_service_ids:
                if res.extention_number_id.implementation_application_number_id == rec.id:
                    res.extention_number_id.implementation_application_number_id = False

    @api.model
    def get_email_to(self):
        email_list = []
        purchase_user_group = self.env.ref("purchase.group_purchase_user")
        email_list = [usr.partner_id.email for usr in purchase_user_group.users if usr.partner_id.email]
        # email_list.append()
        account_user_group = self.env.ref("account.group_account_user")
        email_list += [usr.partner_id.email for usr in account_user_group.users if usr.partner_id.email]
        property_user_group = self.env.ref("iwesabe_ppmdc_airport_management.group_property_user")
        email_list += [usr.partner_id.email for usr in property_user_group.users if usr.partner_id.email]
        if self.partner_id.email:
            email_list.append(self.partner_id.email)
        return ",".join(email_list)

    def button_send_mail(self):
        self.ensure_one()
        # template_id = self._find_mail_template()
        template_id = self.env.ref('iwesabe_ppmdc_airport_management.email_send_for_ims_creation_mail')
        model = self.env['ir.model']._get(self._name)
        # if self.lang:
        #     lang = self._render_lang([self.id])[self.id]
        #     template_id = template_id.with_context(lang=lang)
        #     model = model.with_context(lang=lang)
        group_id = self.env.ref('purchase.group_purchase_user')
        purchase_user_list = group_id.users
        new_purchase_user_list = [self.partner_id.id]
        for aa in purchase_user_list:
            if aa.email:
                new_purchase_user_list.append(aa.id)
        print ("purchase_user_list", purchase_user_list)
        ctx = {
            'default_model': 'implementation.service.application',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id.id,
            'default_composition_mode': 'comment',
            'force_email': True,
            'model_description': model.display_name,
            # 'default_partner_ids': [(6, 0, new_purchase_user_list)]
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


class ApplicationServicesModel(models.Model):
    _name = 'service.application.line'
    _rec_name = 'product_id'
    _description = 'Application Services'

    service_application_id = fields.Many2one("implementation.service.application")
    product_id = fields.Many2one("product.template", string="Service")
    points = fields.Float(string="Points/month")
    points_ref = fields.Float(string="points Ref")
    # product_vlan_ids = fields.Many2one("product.product", string="VLAN")
    product_vlan_id = fields.Many2one('vlan.vlan.line', string="VLAN")
    quantity = fields.Float(string="Quantity")
    location_id = fields.Many2one("property.property", string="Location")

    rent = fields.Float(string="Rent")
    total = fields.Float(string="Total")

    authority = fields.Char(string="Authority")
    note = fields.Char(string="Note")
    # update service_application_line set product_vlan_ids=NULL

    @api.constrains('points', 'points_ref')
    def _check_points_ref(self):
        for rec in self:
            if rec.points_ref > 0 and rec.points > rec.points_ref:
                raise ValidationError(_('Please Available Points'))

    @api.onchange('product_id')
    def get_product_vlan_variant(self):
        for rec in self:
            variant_list = []
            for line in rec.product_id.product_variant_ids:
                variant_list.append(line.id)
            return {'domain': {'product_vlan_ids': [('id', 'in', variant_list)]}}


class ApplicationServicesModelRelated(models.Model):
    _name = 'service.application.line.related'
    _rec_name = 'product_id'
    _description = 'Application Services'

    related_service_application_id = fields.Many2one("implementation.service.application")

    product_id = fields.Many2one("product.template", string="Service")
    points = fields.Float(string="Points")
    points_ref = fields.Float(string="points Ref")
    # product_vlan_ids = fields.Many2one("product.product", string="VLAN")
    product_vlan_id = fields.Many2one('vlan.vlan.line', string="VLAN")
    quantity = fields.Float(string="Quantity")
    location_id = fields.Many2one("property.property", string="Location")

    rent = fields.Float(string="Rent")
    total = fields.Float(string="Total")

    authority = fields.Char(string="Authority")
    note = fields.Char(string="Note")
    # update service_application_line set product_vlan_ids=NULL

    @api.constrains('points', 'points_ref')
    def _check_points_ref(self):
        for rec in self:
            if rec.points_ref > 0 and rec.points > rec.points_ref:
                raise ValidationError(_('Please Available Points'))

    @api.onchange('product_id')
    def get_product_vlan_variant(self):
        for rec in self:
            variant_list = []
            for line in rec.product_id.product_variant_ids:
                variant_list.append(line.id)
            return {'domain': {'product_vlan_ids': [('id', 'in', variant_list)]}}


class TelephoneServiceApplicationLine(models.Model):
    _name = 'telephone.service.application.line'
    _rec_name = 'equipment_id'
    _description = 'Telephone Service Application'

    telephone_application_id = fields.Many2one("implementation.service.application")

    equipment_id = fields.Many2one('maintenance.equipment', string='Phone')
    extention_number_id = fields.Many2one('phone.extentaion.numbers', string='Extention Number')
    phone_extention_id = fields.Many2one('phone.extention', string='Phone Extention Service')
    location_id = fields.Many2one("property.property", string="Location")
    authority = fields.Char(string="Authority")
    note = fields.Char(string="Note")
    replacement_equipnment_id = fields.Many2one('maintenance.equipment', string='Replacement Equipments')
    type_of_replacement = fields.Selection([('upgrade', 'Upgrade'), ('damaged', 'Damaged')], string="TYpe of Relacement")
    type_of_request = fields.Selection(related="telephone_application_id.type_of_request", string="Type Of Request", store=True)



    @api.onchange('phone_extention_id')
    def filter_extention_number_id(self):
        # lines = []
        # for rec in self.phone_extention_id.extention_number_ids:
        #     lines.append(rec.id)
        # return {'domain': {'extention_number_id': [('id', 'in', lines)]}}
        self.extention_number_id = False

    @api.model
    def maintenance_request(self):
        pass


class TelephoneServiceApplicationLineRelated(models.Model):
    _name = 'telephone.service.application.line.related'
    _rec_name = 'equipment_id'
    _description = 'Telephone Service Application'

    related_telephone_application_id = fields.Many2one("implementation.service.application")

    equipment_id = fields.Many2one('maintenance.equipment', string='Model')
    extention_number_id = fields.Many2one('phone.extentaion.numbers', string='Extention Number')
    phone_extention_id = fields.Many2one('phone.extention', string='Phone Extention Service')
    location_id = fields.Many2one("property.property", string="Location")
    authority = fields.Char(string="Authority")
    note = fields.Char(string="Note")
    replacement_equipnment_id = fields.Many2one('maintenance.equipment', string='Replacement Equipments')
    type_of_replacement = fields.Selection([('upgrade', 'Upgrade'), ('damaged', 'Damaged')], string="TYpe of Relacement")

    @api.onchange('phone_extention_id')
    def filter_extention_number_id(self):
        # lines = []
        # for rec in self.phone_extention_id.extention_number_ids:
        #     lines.append(rec.id)
        # return {'domain': {'extention_number_id': [('id', 'in', lines)]}}
        self.extention_number_id = False

    @api.model
    def maintenance_request(self):
        pass

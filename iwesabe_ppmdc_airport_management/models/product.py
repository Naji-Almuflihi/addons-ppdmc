# -*- coding:utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_furniture = fields.Boolean(string="Is Furniture")
    is_vlan = fields.Boolean(string="VLAN/Internet/Service")
    vlan_line_ids = fields.One2many("vlan.vlan.line", "product_tmpl_id", string="VLAN Detail")
    is_phone_extention_servie = fields.Boolean('Phone Extention Service')
    phone_extention_number_ids = fields.One2many('phone.extentaion.numbers.vlan', 'product_id')



class VlanVlaneModel(models.Model):
    _name = 'vlan.vlan.line'
    _description = 'VLAN Lines'

    @api.depends('product_tmpl_id')
    def get_name_product(self):
        for res in self:
            res.name = ""
            if res.product_tmpl_id:
                res.name = res.product_tmpl_id.name

    name = fields.Char(string="Name", default="New", index=True, readonly=True, compute="get_name_product")
    minimum_point = fields.Float(string="Minimum Point")
    maximum_point = fields.Float(string="Maximum Point")
    rent_type_id = fields.Many2one('rent.type', string='Season Rent')
    price = fields.Float(string="Price")
    product_tmpl_id = fields.Many2one("product.template", string="Product")
    product_id = fields.Many2one('product.product', string="Product")
    # tenancy_service_quotation_id = fields.Many2one("tenancy.service.contract", string="Tenancy Service Quotation")
    phone_extention_number_ids = fields.One2many('phone.extentaion.numbers.vlan', 'vlan_id')
    is_reserved = fields.Boolean(string="Reserved")
    price_per_point = fields.Boolean(string="Price Per Point")



    @api.onchange('price_per_point')
    def get_product_price(self):
        if self.price_per_point:
            self.price = self.product_tmpl_id.list_price

    @api.constrains('minimum_point', 'maximum_point')
    def constrain_maximum_point(self):
        for rec in self:
            if rec.maximum_point < rec.minimum_point:
                raise ValidationError(_('Maximum Point must be less than Minimum Point'))


class PhoneExtentionNumbersVlan(models.Model):
    _name = 'phone.extentaion.numbers.vlan'
    _descripton = 'PhoneExtention Numbers VLAN'

    name = fields.Char(string="Extention Number", required=True)
    reserverd = fields.Boolean(string='reserverd')
    vlan_id = fields.Many2one('vlan.vlan.line', string='VLAN')
    used_by = fields.Char(string="Used By")
    tenancy_id = fields.Many2one('tenant.tenancy', string='Tenancy')
    partner_id = fields.Many2one(related='tenancy_id.tenant_id', string='Tenant', store=True)
    service_contract_id = fields.Many2one('tenancy.service.contract', string='Service Contract')
    product_id = fields.Many2one('product.template', string="Product")
    implemetation_service_applcation_id = fields.Many2one('implementation.service.application', string='Implementation Service Application')
    # service_application_number_id = fields.Many2one('service.application', string="Service Application Number")

    @api.constrains('vlan_id', 'name')
    def check_constrain_vlan_id_name(self):
        for res in self:
            if res.vlan_id and res.name:
                old_id = self.env['phone.extentaion.numbers.vlan'].search([('vlan_id', '=', res.vlan_id.id), ('id', '!=', res.id), ('name', '=', res.name)])
                if old_id:
                    raise UserError(_("Extention Number must be uniqe with Vlan"))

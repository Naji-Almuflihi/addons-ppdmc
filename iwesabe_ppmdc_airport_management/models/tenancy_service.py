# -*- coding:utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class TenancyService(models.Model):
    _name = 'tenancy.service'
    _description = 'Tenancy Service'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    service_contract_id = fields.Many2one('tenancy.service.contract', string='Tenancy')
    product_id = fields.Many2one('product.template', string='Service', required=True)
    product_vlan_id = fields.Many2one("product.attribute.value", string="Vlan")
    rent = fields.Float(string="Rent", track_visibility='onchange')
    quantity = fields.Float(string='Quantity', default=1)
    total = fields.Float(compute='_compute_total', string="Total", store=True)
    service_application_id = fields.Many2one('service.application', string='Service Application')
    property_id = fields.Many2one('property.property', string='Property')
    points = fields.Float(string='Points/month')
    vlan = fields.Char(string="VlAN")
    tenancy_id = fields.Many2one('tenant.tenancy', string='Tenancy')
    location_id = fields.Many2one("property.property", string="Location")
    pricing_type = fields.Selection([('per_package', 'Per Package'), ('per_point', 'Per Point/month')], string="Pricing Type", required=True)
    rent_type_id = fields.Many2one('rent.type',string='Season Rent')
    price = fields.Float(string='Price')

    @api.depends('rent', 'quantity', 'pricing_type')
    def _compute_total(self):
        for record in self:
            if record.pricing_type == 'per_package':
                record.total = record.rent
            if record.pricing_type == 'per_point':
                record.total = record.rent * record.points

    @api.constrains('product_id', 'points')
    def constrains_points(self):
        for rec in self:
            if rec.product_id.is_vlan:
                is_vlan = False
                for vlan in rec.product_id.vlan_line_ids:
                    if vlan.minimum_point <= rec.points <= vlan.maximum_point:
                        is_vlan = True
                    if not is_vlan:
                        raise ValidationError(_('Please Enter Point between Maximum and Minimum Point'))

    @api.onchange('product_id', 'points', 'service_contract_id')
    def filter_product_vlan(self):
        for rec in self:
            rent = 0.0
            property_list = []
            if rec.product_id.is_vlan:
                for vlan in rec.product_id.vlan_line_ids:
                    if vlan.minimum_point <= rec.points <= vlan.maximum_point:
                        rent = vlan.price
                    rec.rent = rent

            for serv in rec.service_contract_id.tenancy_id.property_ids:
                property_list.append(serv.property_id.id)

            return {'domain': {'location_id': [('id', 'in', property_list)]}}

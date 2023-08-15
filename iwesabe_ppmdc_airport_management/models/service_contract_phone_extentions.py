# -*- coding:utf-8 -*-
from odoo import api, fields, models


class ServiceContractPhoneExtention(models.Model):
    _name = 'service.contract.phone.extention'
    _description = 'Service Contract Phone Extention'

    service_contract_id = fields.Many2one('tenancy.service.contract', string='Service Contract')

    property_id = fields.Many2one('property.property', string="Location")
    phone_extention_id = fields.Many2one('phone.extention', string='Phone Extention Service', required=True)
    extention_number_id = fields.Many2one('phone.extentaion.numbers', string='Extention Number')
    equipment_id = fields.Many2one('maintenance.equipment', string='Model')
    number_reserved = fields.Boolean(string="Reserved")
    service_application_id = fields.Many2one('service.application', string='Service Application')
    rent = fields.Float(string="Rent", required=True, track_visibility='onchange')
    quantity = fields.Float(string='Quantity', default=1, required=True)
    total = fields.Float(compute='_compute_total', string="Total", store=True)
    tenancy_id = fields.Many2one('tenant.tenancy', string='Tenancy')
    rent_type_id = fields.Many2one('rent.type',string='Season Rent')
    price = fields.Float(string='Price')

    @api.onchange('phone_extention_id')
    def onchange_phone_extention_id(self):
        if self.phone_extention_id:
            self.rent = self.phone_extention_id.rent

    @api.depends('rent', 'quantity')
    def _compute_total(self):
        for record in self:
            record.total = record.quantity * record.rent

    @api.onchange('property_id')
    def onchange_property_id(self):
        property_ids = []
        if self.service_contract_id.tenancy_id:
            if self.service_contract_id.tenancy_id.property_ids:
                property_ids = [r.property_id.id for r in self.service_contract_id.tenancy_id.property_ids]

            res = {}
            res['domain'] = {'property_id': [('id', 'in', property_ids)]}
            return res

    @api.onchange('equipment_id')
    def onchange_equipment_id(self):
        eq_ids = []
        if self.service_contract_id.equipment_ids:
            if self.service_contract_id.equipment_ids:
                eq_ids = [r.equipment_id.id for r in self.service_contract_id.equipment_ids]
            res = {}
            res['domain'] = {'equipment_id': [('id', 'in', eq_ids)]}
            return res

    def action_reserved_number(self):
        self.extention_number_id.reserverd = True
        self.extention_number_id.tenancy_id = self.service_contract_id.tenancy_id.id
        self.extention_number_id.service_contract_id = self.service_contract_id.id
        self.number_reserved = True

    def action_unreserved_number(self):
        self.extention_number_id.reserverd = False
        self.extention_number_id.tenancy_id = False
        self.number_reserved = False

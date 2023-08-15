# -*- coding:utf-8 -*-
from odoo import api, fields, models


class TenancyEquipemnt(models.Model):
    _name = 'tenancy.equipment'
    _description = 'Tenancy.Equipemnt'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    service_contract_id = fields.Many2one('tenancy.service.contract', string='Tenancy')
    equipment_id = fields.Many2one('maintenance.model', string='Model', required=True)
    property_id = fields.Many2one('property.property', string="Location")
    rent = fields.Float(string="Rent", required=True)
    quantity = fields.Float(string='Quantity', default=1, required=True)
    rented = fields.Boolean(string="Rented", store=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    total = fields.Float(compute='_compute_total', string="Total", store=True)
    number_reserved = fields.Boolean(string="Reserved")
    service_application_id = fields.Many2one('service.application', string='Service Application',)
    tenancy_id = fields.Many2one('tenant.tenancy', string='Tenancy')
    rent_type_id = fields.Many2one('rent.type',string='Season Rent')
    price = fields.Float(string='Price')

    authority = fields.Char(string="Authority")
    note = fields.Char(string="Note")

    @api.depends('rent', 'quantity')
    def _compute_total(self):
        for record in self:
            record.total = record.quantity * record.rent

    # @api.onchange('equipment_id')
    # def onchange_equipment_id(self):
    #     self.rent = self.equipment_id.rent

    def action_rented(self):
        if self.equipment_id:
            self.write({'rented': True})
            pass

    def action_unrented(self):
        if self.equipment_id:
            self.write({
                'rented': False,
                'tenancy_id': False
            })

    @api.onchange('service_contract_id')
    def onchange_service_contract_id(self):
        if self.service_contract_id.tenancy_id.property_ids:
            property_ids = []
            if self.service_contract_id.tenancy_id.property_ids:
                property_ids = [r.property_id.id for r in self.service_contract_id.tenancy_id.property_ids]
            res = {}
            res['domain'] = {'property_id': [('id', 'in', property_ids)]}
            return res

    def action_reserved_number(self):
        self.equipment_id.rented = True
        self.equipment_id.property_id = self.property_id.id
        self.number_reserved = True

    def action_unreserved_number(self):
        self.equipment_id.rented = False
        self.equipment_id.property_id = False
        self.number_reserved = False

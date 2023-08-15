# -*- coding:utf-8 -*-
from odoo import api, fields, models


class TenancyPhoneExtention(models.Model):
    _name = 'tenancy.phone.extention'
    _description = 'Tenancy Phone Extention'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char(string="Name")
    service_contract_id = fields.Many2one('tenancy.service.contract', string='Tenancy')
    phone_extention_id = fields.Many2one('phone.extention', string='Phone Extention Service', required=True)
    rent = fields.Float(string="Rent", required=True, track_visibility='onchange')
    quantity = fields.Float(string='Quantity', default=1, required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    total = fields.Float(compute='_compute_total', string="Total", store=True)
    extention_number_ids = fields.Many2many('phone.extentaion.numbers', string='Extention Number')
    property_id = fields.Many2one('property.property', string="Location")
    equipment_id = fields.Many2one('maintenance.equipment', string='Model')
    number_reserved = fields.Boolean(string="Reserved")

    def action_reserved_number(self):
        self.extention_number_id.reserverd = True
        self.number_reserved = True

    def action_unreserved_number(self):
        self.extention_number_id.reserverd = False
        self.number_reserved = False

    @api.depends('rent', 'quantity')
    def _compute_total(self):
        for record in self:
            record.total = record.quantity * record.rent

    @api.onchange('phone_extention_id')
    def onchange_phone_extention_id(self):
        self.rent = self.phone_extention_id.rent
        res = {}
        res['domain'] = {'extention_number_ids': [('id', 'in', self.phone_extention_id.extention_number_ids.ids)]}
        return res

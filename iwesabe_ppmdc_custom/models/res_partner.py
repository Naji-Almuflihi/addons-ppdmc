# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    airline_name = fields.Char('Airline Name')
    customer_type_id = fields.Many2one('customer.type', string="Customer Type")

    @api.model
    def create(self, values):
        if self.env.context.get('res_partner_search_mode') == 'customer':
            values['ref'] = self.env['ir.sequence'].get('res.partner.customer') or ' '
        if self.env.context.get('res_partner_search_mode') == 'supplier':
            values['ref'] = self.env['ir.sequence'].get('res.partner.vendor') or ' '
        res = super(ResPartner, self).create(values)
        return res


class CustomerType(models.Model):
    _name = 'customer.type'

    name = fields.Char('Name')

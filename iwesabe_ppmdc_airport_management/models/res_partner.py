# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details

import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    arabic_name = fields.Char(
        string="Arabic Name"
    )
    tenant = fields.Boolean(
        string='Tenant',
        help="Check this box if this contact is a tenant.")
    occupation = fields.Char(
        string='Occupation',
        size=20)
    agent = fields.Boolean(
        string='Agent',
        help="Check this box if this contact is a Agent.")
    mobile = fields.Char(
        string='Mobile',
        size=15)
    tenant_ids = fields.One2many(
        'tenant.tenancy', 
        'tenant_id',
        string="Property")

    tenant_count = fields.Integer(
        strint="Tenant Count",
        compute='_compute_tenant',
        store=True )

    tenant_code = fields.Char(string='Tenant Code', default='/', copy=False)
        
    @api.depends('tenant_ids')
    def _compute_tenant(self):
        for record in self:
            record.tenant_count = len(record.tenant_ids.ids)

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        if res.tenant_code == '/':
            if res.customer_rank > 1:
                res.tenant_code = self.env['ir.sequence'].next_by_code('tenant.customer.code') or '/'
            elif res.supplier_rank > 1:
                res.tenant_code = self.env['ir.sequence'].next_by_code('tenant.vendor.code') or '/'
            else:
                res.tenant_code = self.env['ir.sequence'].next_by_code('tenant.customer.code') or '/'
        return res
    
    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        tenant_group = \
            self.env.ref('iwesabe_ppmdc_airport_management.group_property_user')
        agent_group = \
            self.env.ref('iwesabe_ppmdc_airport_management.group_property_agent')
        for partner in self:
            if 'tenant' in vals:
                if not partner.tenant:
                    if partner.user_ids.has_group(
                            'iwesabe_ppmdc_airport_management.group_property_user'):
                        partner.user_ids.write(
                            {'groups_id': [(3, tenant_group.id)]})
                else:
                    partner.user_ids.write(
                        {'groups_id': [(4, tenant_group.id)]})
            if 'agent' in vals:
                if not partner.agent:
                    if partner.user_ids.has_group(
                            'iwesabe_ppmdc_airport_management.group_property_agent'):
                        partner.user_ids.write(
                            {'groups_id': [(3, agent_group.id)]})
                else:
                    partner.user_ids.write(
                        {'groups_id': [(4, agent_group.id)]})
        return res

    @api.constrains('mobile')
    def _check_value(self):
        """
        Check the mobile number in special formate if you enter wrong
        mobile formate then raise ValidationError
        """
        for val in self:
            if val.mobile:
                if re.match(
                        "^\+|[1-9]{1}[0-9]{3,14}$", val.mobile) is not None:
                    pass
                else:
                    raise ValidationError(
                        _('Please Enter Valid Mobile Number!'))

    @api.constrains('email')
    def _check_values(self):
        """
        Check the email address in special formate if you enter wrong
        mobile formate then raise ValidationError
        """
        for val in self:
            if val.email:
                if re.match("^[a-zA-Z0-9._+-]+@[a-zA-Z0-9]+\.[a-zA-Z0-9.]*"
                            "\.*[a-zA-Z]{2,4}$", val.email) is not None:
                    pass
                else:
                    raise ValidationError(_('Please Enter Valid Email Id!'))


    def action_view_property(self):
        actions = self.env.ref('iwesabe_ppmdc_airport_management.action_tenancy_tenant_view').read()[0]
        actions['domain'] = [('tenant_id', '=', self.id)]
        actions['context'] = {'create':False}
        return actions


class ResUsers(models.Model):
    _inherit = "res.users"



class ResCompany(models.Model):
    _inherit = 'res.company'

    default_password = fields.Char(
        string='Default Password')

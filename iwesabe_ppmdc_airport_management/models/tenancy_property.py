# -*- coding:utf-8 -*-
from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError

class TenancyProperty(models.Model):
    _name = 'tenancy.property'
    _description = 'Tenancy Proprty'

    amount_residual = fields.Float(string="Invoice Amount Due", related='tenancy_id.amount_residual')
    amount_total = fields.Float(string="Invoice Total Amount", related='tenancy_id.amount_total')
    paid_amount = fields.Float(string="Invoice Paid Amount", related='tenancy_id.paid_amount')

    property_id = fields.Many2one(
        'property.property',
        string='Proprty',
        required=True

    )


    tenancy_id = fields.Many2one(
        'tenant.tenancy',
        string='tenancy',
    )


    partner_id = fields.Many2one(comodel_name="res.partner",string="Tenant",related='tenancy_id.tenant_id')


    date_start = fields.Date(
        string="Start Date",
        # related='tenancy_id.date_start',
        # readonly=True,
        # store=True
        
    )
    date_end = fields.Date(
        string="End Date",
        # related='tenancy_id.date_end',
        # readonly=True,
        # store=True
        
    )
    rent_type_id = fields.Many2one(
        'rent.type',
        string='Season Rent',
     
    )
    rent = fields.Float(
        string="Rent",
        required=True,

    )
    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        required=True,
        default=lambda self: self.env.user.company_id
    )
    gfa_meter = fields.Float(
        string="GFQ(M2)",
        required=True
        
    )
    total = fields.Float(
        string='Total',
        compute='_compute_total',
        store=True
    )
    season_year_id = fields.Many2one(
        'season.year',
        string="Season Year"    
    )
    service_application_id = fields.Many2one(
        'service.application',
        string='Service Application',
    )
    vat_ids = fields.Many2many(comodel_name="account.tax",string="Tax")




    @api.depends('gfa_meter', 'rent')
    def _compute_total(self):
        for record in self:
            record.total = record.gfa_meter * record.rent



    def _prepare_invoice_line(self):
        if not self.company_id.income_account:
            raise ValidationError(_('Please insert income account in configuration!!'))
        return {
            'name': self.property_id.name,
            'account_id': self.company_id.income_account.id,
            'price_unit': self.rent,
            'quantity': self.gfa_meter,
            'product_uom_id': self.env.ref('uom.product_uom_meter').id,
        }

    @api.onchange('property_id')
    def onchange_property_id(self):
        if self.property_id.rent_price_ids:
            for line in self.property_id.rent_price_ids:
                if self.rent_type_id.id == line.rent_type_id.id:
                    self.rent = line.rent
                    self.gfa_meter = line.gfa_meter
                    break
        else:
            self.rent = 0.0
            self.gfa_meter = 0.0
    
    # @api.onchange('service_application_id')
    # def onchange_service_application_id(self):
    #     if self.service_application_id.rent_price_ids:
    #         for line in self.service_application_id.rent_price_ids:
    #             if self.rent_type_id.id == line.rent_type_id.id:
    #                 self.rent = line.rent
    #                 self.gfa_meter = line.gfa_meter
    #                 break
    #     else:
    #         self.rent = 0.0
    #         self.gfa_meter = 0.0

                


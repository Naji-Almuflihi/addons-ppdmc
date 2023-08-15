# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError

from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class Property(models.Model):
    _inherit = 'property.property'

    maintenance_id = fields.Many2one(comodel_name="maintenance.request", string="Maintenance", compute='get_maintenance' )
    maintenance_count = fields.Integer(string="", required=False, compute='get_maintenance_count')

    under_maintain = fields.Boolean(string="",compute='get_maintenance'  )



    @api.depends()
    def get_maintenance(self):
        self.under_maintain = False
        self.maintenance_id = False
        for rec in self.env['maintenance.request'].search([('property_id', '=', self.id)]):
            self.maintenance_id = rec.id
            if not rec.stage_id.done:
                self.under_maintain = True

    @api.depends()
    def get_maintenance_count(self):
        self.maintenance_count = self.env['maintenance.request'].search_count([('property_id', '=', self.id)])


    def create_maintenance(self):
        maintenance = self.env['maintenance.request']
        maintenance_created = maintenance.create({
            'name': self.name,
            'property_id': self.id,
        })

    def action_open_related_maintenance(self):
        return {
            'name': 'Maintenance Requests ',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'maintenance.request',
            'domain': [('property_id', '=', self.id)],
            'target': 'current',
        }




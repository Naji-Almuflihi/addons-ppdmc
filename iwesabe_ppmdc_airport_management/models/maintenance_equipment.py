# -*- coding:utf-8 -*-
from odoo import api, fields, models


class MaintenanceModel(models.Model):
    _name = 'maintenance.model'

    name = fields.Char(string="Model", required=True, copy=False)
    code = fields.Char(string="COde", required=True, copy=False)


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    model = fields.Many2one('maintenance.model', string="Model")
    rented = fields.Boolean(string="Rented", track_visibility='onchange', readonly=True, store=True)
    location_id = fields.Many2one('property.property', string='Location')
    property_id = fields.Many2one('property.property', string='Property', readonly=True, store=True)
    is_equipment = fields.Boolean(string="Phone")

    main_zone_location_id = fields.Many2one("zone.location", string="Area/Zone Location/Main")
    module_property_zone_id = fields.Many2one("property.zone", string="Zone/ Module")

    @api.onchange('property_type_id')
    def onchange_property_type(self):
        lines = []
        for prop in self.env['property.property'].search([('property_type_id', '=', self.property_type_id.id)]):
            lines.append(prop.id)
        return {'domain': {'location_id': [('id', 'in', lines)]}}


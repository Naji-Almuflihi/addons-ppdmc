from odoo import models, fields, api


class ZoneLocationModel(models.Model):
    _name = 'zone.location'
    _rec_name = 'name'
    _description = 'Zone Location'

    name = fields.Char()


class PropertyProperty(models.Model):
    _inherit = 'property.property'

    main_zone_location_id = fields.Many2one("zone.location", string="Zone Location")

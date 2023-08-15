# -*- coding:utf-8 -*-
from odoo import fields, models


class PropertyRoom(models.Model):
    _name = 'property.room'
    _description = 'Property Room'

    name = fields.Char(string="Room Number", required=True)


class PropertyZoneNumber(models.Model):
    _name = 'property.zone.number'
    _description = 'Property Zone Number'

    name = fields.Char(string="Zone Number", required=True)
    zone_id = fields.Many2one('property.zone', string='zone')
    room_ids = fields.Many2many('property.room', string="Rooms")


class PropertyZone(models.Model):
    _name = 'property.zone'
    _description = 'Property Zone'

    name = fields.Char(string="Zone Name", required=True)
    live_id = fields.Many2one('property.live', string='Level')
    room_number_ids = fields.Many2many('property.zone.number.number', string="Zone Number")


class PropertyLive(models.Model):
    _name = 'property.live'
    _description = 'Property Level'

    name = fields.Char(string="Level Number", required=True)
    zone_ids = fields.Many2many('property.zone', string="Zons")


class PropertyZoneNumberNumber(models.Model):
    _name = 'property.zone.number.number'
    _rec_name = 'name'

    name = fields.Char()

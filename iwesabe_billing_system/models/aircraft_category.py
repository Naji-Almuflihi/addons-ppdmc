from odoo import models, fields


class Aircraftcategory(models.Model):
    _name = 'aircraft.category'
    _rec_name = 'name'

    name = fields.Char(string="Name")

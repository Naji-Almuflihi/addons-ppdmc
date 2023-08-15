from odoo import models, fields, api
class SiteModel(models.Model):
    _name = 'site.site'
    _rec_name = 'name'
    _description = 'Site Page'

    name = fields.Char(string="Name")


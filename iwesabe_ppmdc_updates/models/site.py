# -*- coding: utf-8 -*-
from odoo import models, fields


class SupplierSite(models.Model):
    _name = 'site.solution'
    _rec_name = "site_supplier_name"

    # project_id = fields.Many2one(comodel_name="project.project")
    site_supplier_name = fields.Char(string="Supplier Site Type")
    code = fields.Integer(string="Code")

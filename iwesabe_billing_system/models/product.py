from odoo import models, fields, api


class Products(models.Model):
    _inherit = 'product.template'

    arabic_name = fields.Char(string="Arabic Name", required=False)
    is_credit_note = fields.Boolean(string="Is Credit Note")
    is_ams = fields.Boolean(string="AMS")


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_credit_note = fields.Boolean(string="Is Credit Note")
    is_ams = fields.Boolean(string="AMS")

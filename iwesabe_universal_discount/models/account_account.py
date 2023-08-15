
from odoo import models, fields


class Company(models.Model):
    _inherit = "res.company"

    enable_discount = fields.Boolean(string="Activate Universal Discount")
    sales_discount_account = fields.Many2one('account.account', string="Sales Discount Account")
    purchase_discount_account = fields.Many2one('account.account', string="Purchase Discount Account")


class KSResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_discount = fields.Boolean(string="Activate Universal Discount", related='company_id.enable_discount', readonly=False)
    sales_discount_account = fields.Many2one('account.account', string="Sales Discount Account", related='company_id.sales_discount_account', readonly=False)
    purchase_discount_account = fields.Many2one('account.account', string="Purchase Discount Account", related='company_id.purchase_discount_account', readonly=False)

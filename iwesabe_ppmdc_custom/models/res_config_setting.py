# -*- coding:utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    equipment_income_account = fields.Many2one('account.account', 'Income Account')


class ConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    equipment_income_account = fields.Many2one('account.account', 'Income Account', related='company_id.equipment_income_account', readonly=False)

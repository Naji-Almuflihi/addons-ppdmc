# -*- coding:utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    income_account = fields.Many2one('account.account', 'Income Account')
    expense_account = fields.Many2one('account.account', 'Expense Account')
    phone_income_account = fields.Many2one('account.account', 'Phone Income Account')
    equipment_income_account = fields.Many2one('account.account', 'Equipment Income Account')
    service_income_account = fields.Many2one('account.account', 'Service Contract Income Account')
    cancellation_tenancy_approval_id = fields.Many2one("res.users", string="Cancellation Tenancy Approval User")


class ConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    income_account = fields.Many2one(related='company_id.income_account', readonly=False)
    expense_account = fields.Many2one(related='company_id.expense_account', readonly=False)
    phone_income_account = fields.Many2one(related='company_id.phone_income_account', readonly=False)
    equipment_income_account = fields.Many2one(related='company_id.equipment_income_account', readonly=False)
    service_income_account = fields.Many2one(related='company_id.service_income_account', readonly=False)

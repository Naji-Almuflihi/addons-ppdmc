# -*- coding:utf-8 -*-
from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    tenancy_equipment_id = fields.Many2one('tenancy.equipment', string='Tenancy Equipment')
    invoice_date = fields.Date(string='Invoice/Bill Date', readonly=True, index=True, copy=False, default=fields.Date.context_today, states={'draft': [('readonly', False)]})
    ref = fields.Char(string='Reference', copy=False, tracking=True, readonly=True, states={'draft': [('readonly', False)]})
    narration = fields.Text(string='Terms and Conditions', readonly=True, states={'draft': [('readonly', False)]})

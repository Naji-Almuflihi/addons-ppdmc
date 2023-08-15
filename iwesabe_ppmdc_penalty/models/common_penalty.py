# -*- coding: utf-8 -*-
##############################################################################
#
#    Global Creative Concepts Tech Co Ltd.
#    Copyright (C) 2018-TODAY iWesabe (<http://www.iwesabe.com>).
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, api, fields


class CommonPenalty(models.Model):
    _name = 'common.penalty'
    _description = 'Common Penalty'
    _inherit = 'mail.thread'

    name = fields.Char(string='Name')
    common_penalty_line_ids = fields.One2many('common.penalty.line', 'common_penalty_id',
                                              string="Common Penalty Description")
    month = fields.Char(string='Month')
    contract_id = fields.Many2one('contract.contract', string="Contract")


class CommonPenaltyLine(models.Model):
    _name = 'common.penalty.line'

    common_penalty_id = fields.Many2one('common.penalty', string="Common Penalty")
    description_id = fields.Many2one('penalty.item', string="Description")
    no_of_incidents = fields.Integer(string='No. of Incidents & Failure of Reports/Instructions')
    penalty_amount = fields.Integer(string='Penalty Amount', related="description_id.amount")
    total_amount_penalty = fields.Integer(string='Total Penalty SAR', compute='_compute_total_amount_penalty',
                                          store=True)
    penalty_per_day = fields.Integer(string='Penalty P/DAY (SAR)')
    no_of_days_absent = fields.Integer(string='No. of days Absent')

    @api.depends('penalty_per_day', 'no_of_days_absent')
    def _compute_total_amount_penalty(self):
        for line in self:
            if line.no_of_incidents and line.penalty_amount:
                line.total_amount_penalty = line.no_of_incidents * line.penalty_amount

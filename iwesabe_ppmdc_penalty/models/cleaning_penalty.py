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


class CleaningPenalty(models.Model):
    _name = 'cleaning.penalty'
    _description = 'Cleaning Penalty'
    _inherit = 'mail.thread'

    name = fields.Char(string='Name')
    cleaning_penalty_line_ids = fields.One2many('cleaning.penalty.line', 'cleaning_penalty_id',
                                                string="Cleaning Penalty Description")
    month = fields.Char(string='Month')
    contract_id = fields.Many2one('contract.contract', string="Contract")


class CleaningPenaltyLine(models.Model):
    _name = 'cleaning.penalty.line'

    cleaning_penalty_id = fields.Many2one('cleaning.penalty', string="Cleaning Penalty")
    position_description_id = fields.Many2one('penalty.item', string="Position Description")
    penalty_per_day = fields.Integer(string='Penalty P/DAY (SAR)', related="position_description_id.amount")
    no_of_days_absent = fields.Integer(string='No. of days Absent')
    total_amount_penalty = fields.Integer(string='Total Amount Penalty', compute='_compute_total_amount_penalty',
                                          store=True)

    @api.depends('penalty_per_day', 'no_of_days_absent')
    def _compute_total_amount_penalty(self):
        for line in self:
            if line.penalty_per_day and line.no_of_days_absent:
                line.total_amount_penalty = line.penalty_per_day * line.no_of_days_absent

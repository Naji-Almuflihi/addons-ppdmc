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
from odoo import models, fields


class ContractContract(models.Model):
    _inherit = "contract.contract"

    contract_penalty_line_ids = fields.One2many('contract.penalty.line', 'contract_id', string="Penalty Line")


class ContractPenalty(models.Model):
    _name = 'contract.penalty.line'
    _description = "Contract Penalty  Line"

    contract_id = fields.Many2one('contract.contract', string="Contract")
    position_description_id = fields.Many2one('penalty.item', string="Position Description")
    responsible_id = fields.Many2one(related="position_description_id.responsible_id", string="Responsible User", store=True)
    penalty_per_day = fields.Integer(related="position_description_id.amount", string='Penalty P/DAY (SAR)', store=True)

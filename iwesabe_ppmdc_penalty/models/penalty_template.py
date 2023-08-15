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
from odoo import models, api, fields, _
from odoo.exceptions import Warning


class PenaltyTemplate(models.Model):
    _name = 'penalty.template'
    _description = 'Penalty Template'
    _inherit = 'mail.thread'

    sequense = fields.Char()
    name = fields.Char(string='Name')
    penalty_template_line_ids = fields.One2many('penalty.template.line', 'penalty_template_id',
                                                string="Penalty Description")
    month = fields.Char(string='Month')
    contract_id = fields.Many2one('contract.contract', string="Contract")
    currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.company.currency_id.id)
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_compute_total_amount', tracking=4)
    responsible_id = fields.Many2one('res.users', string="Responsible User")
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')], default="draft", string="Status")

    @api.onchange('penalty_template_line_ids')
    def onchange_penalty_template_line_ids(self):
        for line in self.penalty_template_line_ids:
            line.position_description_id.write({'responsible_id':  self.responsible_id.id})

    @api.model
    def create(self, values):
        values['sequense'] = self.env['ir.sequence'].get('penalty.template.seq') or ' '

        res = super(PenaltyTemplate, self).create(values)
        return res

    @api.depends('penalty_template_line_ids.total_amount_penalty')
    def _compute_total_amount(self):
        for penalty in self:
            total = 0.0
            for line in penalty.penalty_template_line_ids:
                total += line.total_amount_penalty
            penalty.update({
                'amount_total': total,
            })


class PenaltyTemplateLine(models.Model):
    _name = 'penalty.template.line'

    penalty_template_id = fields.Many2one('penalty.template', string="Penalty")
    position_description_id = fields.Many2one('penalty.item', string="Position Description")
    penalty_per_day = fields.Integer(string='Penalty P/DAY (SAR)', related="position_description_id.amount")
    no_of_days_absent = fields.Integer(string='No. of days Absent')
    total_amount_penalty = fields.Integer(string='Total Amount Penalty', compute='_compute_total_amount_penalty',
                                          store=True)
    contract_id = fields.Many2one('contract.contract', string="Contract")
    responsible_id = fields.Many2one(related="penalty_template_id.responsible_id", string="Responsible User", store=True)

    @api.model
    def create(self, vals):
        if vals.get('position_description_id'):
            position_description_id = vals.get('position_description_id')
            item_id = self.search([('position_description_id', '=', position_description_id)])
            if item_id:
                raise Warning(_("Penalty Item already exist in this line!"))
            res = super(PenaltyTemplateLine, self).create(vals)
        return res

    @api.depends('penalty_per_day', 'no_of_days_absent')
    def _compute_total_amount_penalty(self):
        for line in self:
            if line.penalty_per_day and line.no_of_days_absent:
                line.total_amount_penalty = line.penalty_per_day * line.no_of_days_absent

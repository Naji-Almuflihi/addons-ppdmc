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


class PenaltySheet(models.Model):
    _name = 'penalty.sheet'
    _description = 'Penalty Sheet'
    _inherit = 'mail.thread'

    name = fields.Char()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, readonly=True)
    responsible_id = fields.Many2one('res.users', string="Responsible User")
    contract_id = fields.Many2one('contract.contract', string="Contract")
    move_id = fields.Many2one('account.move', string="Invoice")
    penalty_total = fields.Float(string="Total", compute="compute_total", store=True)
    penalty_sheet_line_ids = fields.One2many('penalty.sheet.lines', 'sheet_id', string="Sheet Details")
    # display_type = fields.Selection([('section', 'Section'), ('item', 'Item')], default=False)
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')], default="draft", string="Status")

    def action_confirm(self):
        # email_template = self.env.ref('iwesabe_ppmdc_penalty.email_confirm_penalty_sheet')
        self.write({'state': 'confirmed'})
        # if email_template:
        #     email_template.send_mail(self.id)

    @api.depends('penalty_sheet_line_ids.penalty_amount')
    def compute_total(self):
        total = 0.0
        for line in self.penalty_sheet_line_ids:
            total += line.penalty_amount
        self.penalty_total = total

    def reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('penalty.sheet.seq')
        contract = self.env['contract.contract'].browse(vals.get('contract_id'))
        vals.update({'name': name + '/' + contract.name or '/'})
        return super(PenaltySheet, self).create(vals)


class PenaltySheetLines(models.Model):
    _name = 'penalty.sheet.lines'

    sheet_id = fields.Many2one('penalty.sheet')
    item_id = fields.Many2one('penalty.item', string="Item")
    item_amount = fields.Integer('Amount', related="item_id.amount")
    penlty_temp_id = fields.Many2one('penalty.template', string="Template")
    penalty_amount = fields.Integer(compute="compute_penalty_amount", store=True, string="Penalty Amount")
    penalty_uom = fields.Many2one('uom.uom', related="item_id.uom_id", string="UOM")
    absent_days = fields.Integer(string="Number Of absent")

    @api.depends('absent_days', 'item_id.amount')
    def compute_penalty_amount(self):
        for line in self:
            line.penalty_amount = line.absent_days * line.item_id.amount

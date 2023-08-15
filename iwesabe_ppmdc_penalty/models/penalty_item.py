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


class PenaltyItem(models.Model):
    _name = 'penalty.item'
    _description = 'Penalty Item'

    name = fields.Char(string='Name')
    amount = fields.Integer(string='amount')
    uom_id = fields.Many2one('uom.uom', string="Unit of Measure")
    responsible_id = fields.Many2one('res.users', string="User")
    category_name = fields.Char(related="uom_id.category_id.name", store=True)
    penalty_line_id = fields.Many2one('penalty.template.line', string="Penalty Line")

    @api.onchange('uom_id')
    def onchange_uom_id_domain(self):
        # Domain to get working times only UOM
        uom_ids = self.env['uom.uom'].search([('category_id.name', '=', 'Working Time')])
        return {'domain': {'uom_id': [('id', 'in', uom_ids.ids)]}}

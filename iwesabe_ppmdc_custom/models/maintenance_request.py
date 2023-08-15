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
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    @api.depends('equipment_id')
    def get_last_next_action_date(self):
        for res in self:
            res.next_action_date = ""
            if res.equipment_id and res.equipment_id.next_action_date:
                res.next_action_date = res.equipment_id.next_action_date

    spare_part_check = fields.Selection([('yes', 'YES'), ('no', 'NO')], default='no', string='Spare Part')
    next_action_date = fields.Date(string='next preventive maintenance', compute="get_last_next_action_date")

    @api.onchange('stage_id')
    def compute_check_in_progress(self):
        for rec in self:
            if rec.stage_id.id == self.env.ref('maintenance.stage_1').id and not rec.spare_part_check:
                raise ValidationError(_('Please Set Spare Part'))
            return False


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    @api.onchange('repair_eqp_id')
    def _onchange_repair_eqp_id(self):
        if self.repair_eqp_id:
            self.location_id = self.repair_eqp_id.warehouse_location_id

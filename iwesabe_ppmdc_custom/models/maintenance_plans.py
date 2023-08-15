# * coding: utf8 *
##############################################################################
#
#    Global Creative Concepts Tech Co Ltd.
#    Copyright (C) 2018TODAY iWesabe (<http://www.iwesabe.com>).
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

from odoo import models, fields, api


class MaintenancePlans(models.Model):
    _name = 'maintenance.plans'

    name = fields.Char('Name', required=True)
    schedule_date = fields.Date('Schedule Date')
    deadline_date = fields.Date('Deadline Date')
    category_id = fields.Many2one('maintenance.equipment.category', string='Category')
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment')
    status = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('cancel', 'Cancelled')],
                              default='draft', string='Status')

    def action_confirm(self):
        for plans in self:
            self.env['maintenance.request'].create({
                'name': plans.name,
                'schedule_date': plans.schedule_date,
                'deadline_date': plans.deadline_date,
                'category_id': plans.category_id.id,
                'equipment_id': plans.equipment_id.id,
                'maintenance_plan_id': plans.id,
            })
            plans.status = 'confirmed'

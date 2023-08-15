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


class EquipmentLocation(models.Model):
    _inherit = 'equipment.location.change'

    current_location_id = fields.Many2one('property.property', 'Current Location', )

    @api.onchange('equipment_id')
    def action_set_current_location(self):
        if self.equipment_id.rented == True:
            self.update({
                'current_location_id': self.equipment_id.property_id.id
            })
        elif self.equipment_id.dest_loc == True:
            self.update({
                'current_location_id': self.equipment_id.dest_location_id.id
            })
        else:
            self.update({
                'current_location_id': self.equipment_id.location_id.id
            })


class EquipmentLocationMaintenance(models.Model):
    _inherit = 'maintenance.equipment'
    
    dest_location_id = fields.Many2one('property.property', 'Destination Location', )
    dest_loc = fields.Boolean(string="", )
    


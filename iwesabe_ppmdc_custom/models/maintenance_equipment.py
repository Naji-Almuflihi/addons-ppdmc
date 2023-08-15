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
from odoo import models, fields, api
from datetime import datetime


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    @api.depends('system_id', 'sub_system_id', 'category_id')
    def get_name_from_detail(self):
        for res in self:
            # if res.number == 'New':
            #     res.number = self.env['ir.sequence'].next_by_code('maintenance.equipment', sequence_date=None) or _('New')
            name = []
            if res.system_id and res.system_id.code:
                name.append(res.system_id.code)
            if res.sub_system_id and res.sub_system_id.code:
                name.append(res.sub_system_id.code)
            if res.category_id and res.category_id.code:
                name.append(res.category_id.code)
            if res.category_id.equipment_count > 0:
                name.append(str(res.category_id.equipment_count))
            # name.append(res.number)
            final_name = "-".join(name)
            # res.name = final_name
            res.equipment_id = final_name

    number = fields.Char(string="Number", default="New", readonly=True)
    equipment_id = fields.Char(string="Equipment ID", compute="get_name_from_detail")
    equipment_make = fields.Char(string="Make")
    equipment_tag = fields.Char(string="Tag")
    area_description = fields.Text(string="Area Description")
    item_type_id = fields.Many2one('equipment.item.type', string="Item Type")
    equipment_location_id = fields.Many2one('equipment.location', string="Equipment Location")
    # equipment_meter_id = fields.Many2one('equipment.meter', string="Equipment Meter")
    # equipment_z_id = fields.Many2one('equipment.z', string="Equipment Z")
    # equipment_room_id = fields.Many2one('equipment.room', string="Equipment Room")
    voltage_final = fields.Char(string="Voltage Final")
    amps_final = fields.Char(string="AMPS Final")
    frequency_final = fields.Char(string="Frequency Final")
    watts_final = fields.Char(string="Watts Final")
    phase_final = fields.Char(string="Phase Final")
    btu_final = fields.Char(string="BTU Final")
    hp_final = fields.Char(string="HP Final")
    psi_final = fields.Char(string="PSI Final")
    rpm_final = fields.Char(string="RPM Final")
    ip_address = fields.Char(string="IP Address")
    mac_address = fields.Char(string="MAC Address")

    rent = fields.Float(string="Rent")
    owned_by_id = fields.Many2one('res.partner', string="Owned By")
    warehouse_location_id = fields.Many2one('stock.location', string="Warehouse")
    system_cat_id = fields.Many2one('system.category', string="System Category")
    # equipment_assign_to = fields.Selection([('other', 'Other')], string='Used By', required=True, default="other")
    kia_equip = fields.Char(string='KAIA Equip# No#')
    device_activation = fields.Boolean('Device Activation')
    property_type_id = fields.Many2one('property.type', string="Location Type/Sub1")
    site_location = fields.Char('Site Location')
    fdr_number = fields.Char('FDR Number')
    model_number = fields.Char('Model Number')
    system_id = fields.Many2one('equipment.system', string="System")
    sub_system_id = fields.Many2one('sub.system', string="Sub System")
    # department_id = fields.Many2one('hr.department', string="Responsible Department")

    # @api.onchange('system_cat_id')
    # def _onchange_system_cat_id(self):
    #     if self.system_cat_id:
    #         return {'domain': {
    #             'sub_system_id': [('id', 'in', [r.id for r in self.system_cat_id.sub_system_cat_id])]
    #         }}

    @api.onchange('category_id')
    def _onchange_category_id(self):
        self.technician_user_id = self.category_id.technician_user_id
        self.department_id = self.category_id.department_id


class MaintenanceEquipmentCategory(models.Model):
    _inherit = 'maintenance.equipment.category'

    department_id = fields.Many2one('hr.department', string="Responsible Department")
    code = fields.Char(string="Code", copy=False)


class SystemCategory(models.Model):
    _name = 'system.category'
    _description = "System Category"

    name = fields.Char('Name', required=True, copy=False)
    code = fields.Char(string="Code", required=True, copy=False)
    eq_system_ids = fields.Many2one('equipment.system', string="System")


class EquipmentSystem(models.Model):
    _name = 'equipment.system'
    _description = 'Equipment System'

    name = fields.Char(string="Name", required="True")
    code = fields.Char(string="Code", required=True, copy=False)
    system_cat_id = fields.Many2one('system.category', string="System Category")


class SubSystem(models.Model):
    _name = 'sub.system'
    _description = 'Sub System'

    name = fields.Char(string="Sub System", required=True, copy=False)
    code = fields.Char(string="Code", required=True, copy=False)
    system_id = fields.Many2one('equipment.system', string="System")


class EquipmentItemType(models.Model):
    _name = "equipment.item.type"
    _description = "Equipment Item Type"

    name = fields.Char(string="Name", required=True, copy=False)
    code = fields.Char(string="Code", required=True, copy=False)


class EquipmentLocation(models.Model):
    _name = "equipment.location"
    _description = "Equipment Location"

    name = fields.Char(string="Name")
    site = fields.Many2one('equipment.site', string="Site")
    level = fields.Char('Level')
    module = fields.Char('Module')
    zone = fields.Char('Zone')
    room = fields.Char('Room')


class EquipmentSite(models.Model):
    _name = "equipment.site"
    _description = "Equipment Site"

    name = fields.Char(string="Site Name")


#
#
# class EquipmentM(models.Model):
#     _name = "equipment.meter"
#
#     name = fields.Char(string="Name")


# class EquipmentZ(models.Model):
#     _name = "equipment.z"
#
#     name = fields.Char(string="Name")
#
#
# class EquipmentRoom(models.Model):
#     _name = "equipment.room"
#
#     name = fields.Char(string="Name")

class EquipmentLocationChange(models.Model):
    _name = 'equipment.location.change'
    _rec_name = 'equipment_id'

    equipment_id = fields.Many2one('maintenance.equipment', 'Equipment')
    current_location_id = fields.Many2one('property.property', 'Current Location')
    destination_location_id = fields.Many2one('property.property', 'Destination Location')
    date = fields.Date('Date', required=True, default=fields.Date.context_today)
    approval_date = fields.Date('Approval Date')
    approval_user_id = fields.Many2one('res.users', 'Approved By')
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], default='draft')
    note = fields.Text('Note')

    @api.onchange('equipment_id')
    def _onchange_equipment_id(self):
        if self.equipment_id:
            self.current_location_id = self.equipment_id.location

    def approve_location_change(self):
        for rec in self:
            if rec.equipment_id:
                destination_location_id = rec.destination_location_id
                rec.equipment_id.write({'location': destination_location_id.id})
                rec.approval_date = datetime.today()
                rec.approval_user_id = self.env.user.id
                rec.state = 'done'

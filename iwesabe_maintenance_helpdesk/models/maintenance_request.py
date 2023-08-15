# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    help_desk_id = fields.Many2one(comodel_name="helpdesk.ticket", string="", required=False, )
    property_id = fields.Many2one(comodel_name="property.property", string="Location Number",)
    property_type_id = fields.Many2one('property.type', string='Location Type / Sub1')
    sub_2 = fields.Char(string="Sub2")


    @api.onchange('equipment_category_id','property_type_id','system_category_id','property_id',
                  'main_zone_location_id','module_porperty_zone_id')
    def filter_equipment_value(self):
        lines=[]
        lines_property=[]

        equipment_record=self.env['maintenance.equipment'].search([])
        property_record=self.env['property.property'].search([])

        for prop in property_record:
            if (self.property_type_id.id == prop.property_type_id.id or not self.property_type_id)\
                and (self.main_zone_location_id.id == prop.main_zone_location_id.id or not self.main_zone_location_id)\
                and (self.module_porperty_zone_id.id == prop.zone_id.id or not self.module_porperty_zone_id):
                lines_property.append(prop.id)


        for equip in equipment_record:

            if (self.equipment_category_id.id==equip.category_id.id or not self.equipment_category_id) \
                    and (self.property_type_id.id == equip.property_type_id.id or not self.property_type_id)\
                    and (self.system_category_id.id==equip.system_cat_id.id or not self.system_category_id) \
                    and (self.property_id.id==equip.location_id.id or not self.property_id) \
                    and (self.main_zone_location_id.id == equip.main_zone_location_id.id or not self.main_zone_location_id)\
                    and (self.module_porperty_zone_id.id == equip.module_property_zone_id.id or not self.module_porperty_zone_id):
                lines.append(equip.id)



        return {
            'domain': {'property_id':[('id', 'in', lines_property)],'equipment_id': [('id', 'in', lines)],}
        }
from odoo import models, fields, api


class RepairOrderInherit(models.Model):
    _inherit = 'repair.order'

    maintenance_id = fields.Many2one(comodel_name="maintenance.request", string="Maintenance Request")
    location_property_id = fields.Many2one(comodel_name="property.property", string="Location Property")


class RepairLineInherit(models.Model):
    _inherit = 'repair.line'

    @api.onchange('type')
    def _get_location_id_value(self):
        if self.type == 'add':
            self.location_id = self.repair_id.location_id.id

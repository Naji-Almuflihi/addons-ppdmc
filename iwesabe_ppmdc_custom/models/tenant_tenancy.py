# -*- coding:utf-8 -*-
from odoo import api, fields, models


class TenantTenancy(models.Model):
    _inherit = "tenant.tenancy"

    equipment_ids = fields.One2many('tenancy.equipment', 'tenancy_id', string="Equipmentes")
    equipment_count = fields.Integer(string="Equipment Count", compute='_compute_equipment', store=True)

    @api.depends('equipment_ids')
    def _compute_equipment(self):
        for record in self:
            record.equipment_count = len(record.equipment_ids.ids)

    def action_view_equipment(self):
        actions = self.env.ref('iwesabe_ppmdc_custom.action_tenancy_equipment').read()[0]
        actions['domain'] = [('tenancy_id', '=', self.id)]
        actions['context'] = {'default_tenancy_id': self.id, 'default_partner_id': self.tenant_id.id}
        return actions

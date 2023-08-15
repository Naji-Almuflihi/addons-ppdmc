# -*- coding: utf-8 -*-

from odoo import models, api


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    def action_view_maintenance(self):
        actions = self.env.ref('maintenance.hr_equipment_request_action').read()[0]
        actions['domain'] = [('ticket_id', '=', self.id)]
        return actions

    def action_create_maintenance(self):
        return {
              'res_model': 'maintenance.request',
              'type': 'ir.actions.act_window',
              'view_type': 'form',
              'view_id': self.env.ref('maintenance.hr_equipment_request_view_form').id,
              'view_mode': 'form',
              'target': 'current',
              'context': {'default_ticket_id': self.id, 'create': False}
          }

    def action_create_work_order_request(self):
        return {
              'res_model': 'work.order.request',
              'type': 'ir.actions.act_window',
              'view_type': 'form',
              'view_id': self.env.ref('iwesabe_ppmdc_airport_management.form_view_work_order_request').id,
              'view_mode': 'form',
              'target': 'current',
          }

    # @api.depends('team_id', 'maintenance_id.user_assistant_id', 'maintenance_id')
    def _compute_user_and_stage_ids(self):
        for ticket in self.filtered(lambda ticket: ticket.team_id):
            if not ticket.stage_id or ticket.stage_id not in ticket.team_id.stage_ids:
                ticket.stage_id = ticket.team_id._determine_stage()[ticket.team_id.id]

        for res in self:
            if res.maintenance_id and res.maintenance_id.user_assistant_id:
                res.user_id = res.maintenance_id.user_assistant_id.id

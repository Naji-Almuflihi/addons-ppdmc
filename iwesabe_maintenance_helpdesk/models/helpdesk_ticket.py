# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    sequence = fields.Char(string="Sequence", default=lambda self: _('New'), copy=False, readonly=True)
    property_id = fields.Many2one("property.property", string="Property", required=False, )
    maintenance_id = fields.Many2one("maintenance.request", string="Maintenance", required=False)
    maintenance_count = fields.Integer(string="", compute='get_maintenance_count')

    @api.model
    def create(self, vals):
        if vals.get('sequence', _('New')) == _('New'):
            vals['sequence'] = self.env['ir.sequence'].next_by_code('helpdesk.ticket', sequence_date=fields.Date.today()) or _('New')
        return super(HelpdeskTicket, self).create(vals)

    def name_get(self):
        result = []
        for ticket in self:
            name = ticket.name
            if ticket.sequence:
                name = ticket.name + ' / ' + ticket.sequence
            result.append((ticket.id, name))
        return result

    def get_maintenance_count(self):
        for res in self:
            res.maintenance_count = 0
            res.maintenance_count = self.env['maintenance.request'].search_count([('help_desk_id', '=', res.id)])

    def create_maintenance(self):
        maintenance = self.env['maintenance.request']
        maintenance_created = maintenance.create({
            'name': self.name,
            'property_id': self.property_id.id,
            'help_desk_id': self.id,
        })
        self.write({'maintenance_id': maintenance_created.id})

    def action_open_related_maintenance(self):
        return {
            'name': 'Maintenance Requests ',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'maintenance.request',
            'domain': [('help_desk_id', '=', self.id)],
            'target': 'current',
        }




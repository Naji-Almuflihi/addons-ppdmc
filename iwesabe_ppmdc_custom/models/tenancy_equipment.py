# -*- coding:utf-8 -*-
from odoo import _, api, fields, models

from datetime import datetime

from odoo.exceptions import ValidationError


class TenancyEquipemnt(models.Model):
    _name = 'tenancy.equipment'
    _description = 'Tenancy.Equipemnt'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char(string="Name", required=True)
    date = fields.Date(string="Date", default=fields.Date.today())
    date_start = fields.Date(string="Start Date", required=True)
    date_end = fields.Date(string="End Date", required=True, track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment', required=True, domain="[('rented', '=', False)]")
    tenancy_id = fields.Many2one('tenant.tenancy', string='Tenancy', required=True)
    state = fields.Selection([('draft', 'Draft'), ('open', 'In Progress'), ('pending', 'To Renew'), ('close', 'Closed'), ('cancelled', 'Cancelled')], string="Status", default='draft', track_visibility='onchange')
    rent = fields.Float(string="Rent", required=True)
    rented = fields.Boolean(string="Rented", related='equipment_id.rented', readonly=True, store=True)
    invoice_ids = fields.One2many('account.move', 'tenancy_equipment_id', string="Invoice")
    invoice_count = fields.Integer(string="Invoice count", compute='_compute_invoice_count', store=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for record in self:
            record.invoice_count = len(record.invoice_ids.ids)

    @api.onchange('equipment_id')
    def onchange_equipment_id(self):
        self.rent = self.equipment_id.rent

    def action_rented(self):
        if self.equipment_id:
            self.equipment_id.write({
                    'rented': True,
                    'tenancy_id': self.tenancy_id.id,
                    'location_id': self.tenancy_id.property_id.location_id.id
               })

    def action_unrented(self):
        if self.equipment_id:
            self.equipment_id.write({'rented': False, 'tenancy_id': False})

    def action_view_invoice(self):
        action = self.env.ref('account.action_move_out_refund_type').read()[0]
        action['domain'] = [('tenancy_equipment_id', '=', self.id)]
        action['context'] = {'default_tenancy_equipment_id': self.id, 'create': False}
        return action

    def get_invloice_lines(self):
        """TO GET THE INVOICE LINES"""
        comapny = self.company_id
        inv_line = {}
        if not comapny.equipment_income_account:
            raise ValidationError(_('Their is not equipment income account !!'))
        for rec in self:
            inv_line = {
                    # 'origin': 'tenancy.rent.schedule',
                    'name': rec.tenancy_id.name,
                    'price_unit': rec.rent or 0.00,
                    'quantity': 1,
                    'account_id': comapny.equipment_income_account.id or False,
                    # 'analytic_account_id': rec.tenancy_id.id or False,
               }
        return [(0, 0, inv_line)]

    def create_invoice(self):
        """
          Create invoice for Rent Schedule.
          @param self: The object pointer
          """
        inv_obj = self.env['account.move']
        for rec in self:
            inv_line_values = rec.get_invloice_lines()
            inv_values = {
                    'partner_id': rec.tenancy_id.tenant_id.id or False,
                    'move_type': 'out_invoice',
                    'tenancy_equipment_id': rec.id or False,
                    'invoice_date': datetime.now() or False,
                    'invoice_line_ids': inv_line_values,
               }
            invoice_id = inv_obj.create(inv_values)
            inv_form_id = self.env.ref('account.view_move_form').id

        return {
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_id': inv_form_id,
            'res_id': invoice_id.id,
            'view_mode': 'form',
            'target': 'current',
          }

    def button_start(self):
        if self.equipment_id:
            self.equipment_id.write({'rented': True, 'tenancy_id': self.tenancy_id.id, 'location_id': self.tenancy_id.property_id.location_id.id})
        return self.write({'state': 'open'})

    def button_close(self):
        self.action_unrented()
        for rec in self:
            rec.write({'state': 'close'})

    def button_set_to_draft(self):
        for rec in self:
            rec.write({'state': 'draft'})

    def button_set_to_renew(self):
        """
          This Method is used to open Tenancy renew wizard.
          @param self: The object pointer
          @return: Dictionary of values.
          """
        self.ensure_one()
        return {
               'name': _('Tenancy Renew Equipment Wizard'),
               'res_model': 'renew.tenancy.equipment',
               'type': 'ir.actions.act_window',
               'view_id': False,
               'view_mode': 'form',
               'view_type': 'form',
               'target': 'new',
               'context': {'default_start_date': self.date_start}
          }

    def button_cancel_tenancy(self):
        """
          This button method is used to Change Tenancy state to Cancelled.
          @param self: The object pointer
          """
        for record in self:
            record.write({'state': 'cancelled'})
        return True

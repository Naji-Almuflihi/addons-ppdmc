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
from odoo.exceptions import UserError, ValidationError


class MaterialPurchaseRequisition(models.Model):
    _name = 'material.purchase.requisition'
    _description = 'Purchase Requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']  # odoo11
    _order = 'id desc'

    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'cancel', 'reject'):
                raise UserError(_('You can not delete Purchase Requisition which is not in draft or cancelled or rejected state.'))
        return super(MaterialPurchaseRequisition, self).unlink()

    @api.model
    def _default_analytic(self):
        related_user_id = self.env.user
        if related_user_id:
            analytic_account_id = self.env['account.analytic.default'].search([('user_id', '=', related_user_id.id)], limit=1)
            if analytic_account_id:
                return analytic_account_id.analytic_id.id
        return self.env['account.analytic.account']

    name = fields.Char(string='Number', index=True, readonly=1)
    state = fields.Selection([
        ('draft', 'New'),
        ('dept_confirm', 'Waiting Department Approval'),
        ('ir_approve', 'waiting inventory approval'),
        ('approve', 'Approved'),
        ('stock', 'Purchase Agreement Created'),
        ('internal_transfer', 'Internal Transfer Created'),
        ('receive', 'Received'),
        ('cancel', 'Cancelled'),
        ('reject', 'Rejected')],
        default='draft', track_visibility='onchange')
    request_date = fields.Date(string='Requisition Date', required=True, default=fields.Date.context_today)
    department_id = fields.Many2one('hr.department', string='Department', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1), required=True, copy=True)
    approve_manager_id = fields.Many2one('hr.employee', string='Department Manager', readonly=True, copy=False)
    reject_manager_id = fields.Many2one('hr.employee', string='Department Manager Reject', readonly=True)
    approve_employee_id = fields.Many2one('hr.employee', string='Approved by', readonly=True, copy=False)
    reject_employee_id = fields.Many2one('hr.employee', string='Rejected by', readonly=True, copy=False)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id, required=True, copy=True)
    location_id = fields.Many2one('stock.location', string='Source Location', copy=True)
    requisition_line_ids = fields.One2many('material.purchase.requisition.line', 'requisition_id', string='Purchase Requisitions Line', copy=True, track_visibility='onchange')
    date_end = fields.Date(string='Requisition Deadline', readonly=True)
    date_done = fields.Date(string='Date Done', readonly=True,)
    managerapp_date = fields.Date(string='Department Approval Date', readonly=True, copy=False)
    manareject_date = fields.Date(string='Department Manager Reject Date', readonly=True)
    userreject_date = fields.Date(string='Rejected Date', readonly=True, copy=False)
    userrapp_date = fields.Date(string='Approved Date', readonly=True, copy=False)
    receive_date = fields.Date(string='Received Date', readonly=True, copy=False)
    reason = fields.Text(string='Reason for Requisitions', required=False, copy=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', copy=True, default=_default_analytic)
    dest_location_id = fields.Many2one('stock.location', string='Destination Location', required=False, copy=True)
    delivery_picking_id = fields.Many2one('stock.picking', string='Internal Picking', readonly=True, copy=False)
    requisiton_responsible_id = fields.Many2one('hr.employee', string='Requisition Responsible')
    employee_confirm_id = fields.Many2one('hr.employee', string='Confirmed by', readonly=True, copy=False)
    confirm_date = fields.Date(string='Confirmed Date', readonly=True, copy=False)

    purchase_order_ids = fields.One2many('purchase.order', 'custom_requisition_id', string='Purchase Ordes')
    custom_picking_type_id = fields.Many2one('stock.picking.type', string='Picking Internal Type', copy=False)
    custom_receipts_type_id = fields.Many2one('stock.picking.type', string='Picking Receipts Type', copy=False)
    inventory_manager_id = fields.Many2one('hr.employee', string="Inventory Approval", copy=False)
    inventory_app_date = fields.Date(string='Inventory Date', readonly=True, copy=False)
    warehouse_id = fields.Many2one("stock.warehouse", string="", compute='get_warehouse', store=True)

    @api.depends('dest_location_id')
    def get_warehouse(self):
        for rec in self:
            warehouse = self.env['stock.warehouse'].search([('lot_stock_id', '=', rec.dest_location_id.id)], limit=1)
            if warehouse:
                for ware in warehouse:
                    rec.warehouse_id = ware.id

    @api.constrains('request_date', 'receive_date', 'date_end')
    def _check_dates(self):
        for requisition in self:
            if requisition.request_date and requisition.receive_date and requisition.date_end:
                if requisition.date_end < requisition.request_date and requisition.receive_date:
                    raise ValidationError(_("Purchase Requisition Deadline should not be less than Requisition Date."))

    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('purchase.requisition.seq')
        vals.update({'name': name})
        res = super(MaterialPurchaseRequisition, self).create(vals)
        return res

    def requisition_confirm(self):
        for rec in self:
            employee_mail_template = self.env.ref('iwesabe_material_purchase_requisitions.email_purchase_requisition_iruser_custom')
            employee_mail_template.sudo().send_mail(self.id)
            msg = 'Dear ' + str(rec.requisiton_responsible_id.name) + 'This Purchase Requisition ' + str(
                    rec.name) + 'Is Need your approval' + ' click here to open: <a target=_BLANK href="/web?#id=' + str(
                    rec.id) + '&view_type=form&model=material.purchase.requisition&action=" style="font-weight: bold">' + str(
                    rec.name) + '</a>'
            if rec.requisiton_responsible_id.user_id:
                partner_ids = [rec.requisiton_responsible_id.user_id.partner_id.id]
                self.sudo().message_post(body=msg, message_type='comment', subtype_xmlid='mail.mt_comment', partner_ids=partner_ids)

            rec.employee_confirm_id = rec.employee_id.id
            rec.confirm_date = fields.Date.today()
            rec.state = 'dept_confirm'

    def requisition_reject(self):
        for rec in self:
            rec.state = 'reject'
            rec.reject_employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            rec.userreject_date = fields.Date.today()

    def manager_approve(self):
        for rec in self:
            manager_mail_template = self.env.ref('iwesabe_material_purchase_requisitions.email_confirm_material_purchase_requistion')
            group = self.env.ref('iwesabe_material_purchase_requisitions.group_purchase_requisition_inventory_manager').users.ids
            dest_loc = self.dest_location_id
            warehouse = self.env['stock.warehouse'].search([('lot_stock_id', '=', dest_loc.id)], limit=1)
            if warehouse:
                warehous_id = False
                for ware in warehouse:
                    warehous_id = ware
                for res in self.env['res.users'].search([]):
                    if warehous_id.id in res.allowed_warehouses_ids.ids:
                        if res.id in group:
                            if manager_mail_template:
                                ctx = self._context.copy()

                                ctx.update({'email_to': res.partner_id.email})
                                manager_mail_template.with_context(ctx).send_mail(self.id, force_send=True)
                                msg = 'Dear ' + str(res.name) + ' This Purchase Requisition ' + str(
                                        rec.name) + ' Need Your Approval' + ' click here to open: <a target=_BLANK href="/web?#id=' + str(
                                        rec.id) + '&view_type=form&model=material.purchase.requisition&action=" style="font-weight: bold">' + str(
                                        rec.name) + '</a>'
                                self.message_post(body=msg, message_type='comment', subtype_xmlid='mail.mt_comment', partner_ids=[res.partner_id.id])

            rec.managerapp_date = fields.Date.today()
            rec.approve_manager_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

            email_iruser_template = self.env.ref('iwesabe_material_purchase_requisitions.email_purchase_requisition')
            email_iruser_template.sudo().send_mail(self.id)
            msg = 'Dear ' + str(rec.employee_id.name) + 'This Purchase Requisition ' + str(
                    rec.name) + 'Is Approved' + ' click here to open: <a target=_BLANK href="/web?#id=' + str(
                    rec.id) + '&view_type=form&model=material.purchase.requisition&action=" style="font-weight: bold">' + str(
                    rec.name) + '</a>'
            self.message_post(body=msg, message_type='comment', subtype_xmlid='mail.mt_comment', partner_ids=[rec.employee_id.user_id.partner_id.id])
            rec.state = 'ir_approve'

    def inventory_approve(self):
        group = self.env.ref('iwesabe_material_purchase_requisitions.group_purchase_requisition_inventory_manager').users.ids
        dest_loc = self.dest_location_id
        warehouse = self.env['stock.warehouse'].search([('lot_stock_id', '=', dest_loc.id)], limit=1)
        current_user = self.env.user
        if warehouse:
            warehous_id = False
            for ware in warehouse:
                warehous_id = ware
            if warehous_id.id in current_user.allowed_warehouses_ids.ids:
                if current_user.id not in group:
                    raise UserError('You can not able to approve , back to your system administrator')
                else:
                    for rec in self:
                        rec.inventory_app_date = fields.Date.today()
                        rec.inventory_manager_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
                        employee_mail_template = self.env.ref('iwesabe_material_purchase_requisitions.email_purchase_requisition_iruser_custom')
                        employee_mail_template.sudo().send_mail(self.id)
                        msg = 'Dear ' + str(rec.employee_id.name) + 'This Purchase Requisition ' + str(
                                rec.name) + 'Is Approved' + ' click here to open: <a target=_BLANK href="/web?#id=' + str(
                                rec.id) + '&view_type=form&model=material.purchase.requisition&action=" style="font-weight: bold">' + str(
                                rec.name) + '</a>'
                        self.message_post(body=msg, message_type='comment', ubtype_xmlid='mail.mt_comment', partner_ids=[rec.employee_id.user_id.partner_id.id])
                        rec.state = 'approve'

    def reset_draft(self):
        for rec in self:
            rec.state = 'draft'

    def _prepare_pick_vals(self, line=False, loc=None, stock_id=False):
        pick_vals = {
            'product_id': line.product_id.id,
            'product_uom_qty': line.qty,
            'product_uom': line.uom.id,
            'location_id': loc.id,
            'location_dest_id': self.dest_location_id.id,
            'name': line.product_id.name,
            'picking_type_id': self.custom_picking_type_id and self.custom_picking_type_id.id or False,
            'picking_id': stock_id.id,
            'custom_requisition_line_id': line.id,
            'company_id': line.requisition_id.company_id.id,
        }
        return pick_vals

    def _prepare_po_line(self, line=False, purchase_order=False):
        po_line_vals = {
            'product_id': line.product_id.id,
            'name': line.product_id.name,
            'product_qty': line.qty,
            'product_uom': line.uom.id,
            'date_planned': fields.Date.today(),
            'price_unit': line.product_id.standard_price,
            'order_id': purchase_order.id,
            'account_analytic_id': self.analytic_account_id.id,
            'custom_requisition_line_id': line.id
        }
        return po_line_vals

    def request_stock(self):
        stock_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        move_id = False
        for rec in self:
            if not rec.location_id:
                raise UserError(_('Select Source location for the picking details.'))
            if not rec.requisition_line_ids:
                raise UserError(_('Please create some requisition lines.'))
            if any(line.requisition_type == 'internal' for line in rec.requisition_line_ids):
                if not rec.location_id.id:
                    raise UserError(_('Select Source location under the picking details.'))
                if not rec.custom_picking_type_id.id:
                    raise UserError(_('Select Picking Type under the picking details.'))
                if not rec.dest_location_id:
                    raise UserError(_('Select Destination location under the picking details.'))

                source_locations = rec.requisition_line_ids.mapped('location_id')
                for loc in set(source_locations):
                    picking_vals = {
                        'partner_id': rec.employee_id.sudo().address_home_id.id,
                        'location_id': loc.id,
                        'location_dest_id': rec.dest_location_id and rec.dest_location_id.id or rec.employee_id.dest_location_id.id or rec.employee_id.department_id.dest_location_id.id,
                        'picking_type_id': rec.custom_picking_type_id.id,  # internal_obj.id,
                        'note': rec.reason,
                        'custom_requisition_id': rec.id,
                        'origin': rec.name,
                        'company_id': rec.company_id.id,

                    }
                    stock_id = stock_obj.sudo().create(picking_vals)
                    delivery_vals = {'delivery_picking_id': stock_id.id}
                    for line in rec.requisition_line_ids.filtered(lambda x: x.requisition_type == 'internal'):
                        if line.location_id == loc:
                            pick_vals = rec._prepare_pick_vals(line, loc, stock_id)
                            move_id = move_obj.sudo().create(pick_vals)
                    rec.write(delivery_vals)
        vals = {}
        purchase_list = []
        for line in self.requisition_line_ids:
            if line.requisition_type == 'internal':
                if move_id:
                    self.state = 'internal_transfer'

            elif line.requisition_type == 'purchase':  # 10/12/2019
                line_vals = {
                    'product_id': line.product_id.id,
                    'product_description_variants': line.description,
                    'product_qty': line.qty,
                    'product_uom_id': line.uom.id,
                    'price_unit': line.product_id.lst_price
                }
                purchase_list.append([0, 0, line_vals])
                vals = {
                    'ordering_date': fields.Date.today(),
                    'custom_requisition_id': self.id,
                    'material_picking_type_id': self.custom_receipts_type_id.id,
                    'picking_type_id': self.custom_picking_type_id.id,
                    'origin': self.name,
                    'requisition_emp_id': self.employee_id.id,
                    'line_ids': purchase_list,
                    'is_requisition_agreement': True,
                }
        if vals:
            self.env['purchase.requisition'].create(vals)
            self.state = 'stock'

    # @api.multi
    def action_received(self):
        for rec in self:
            rec.receive_date = fields.Date.today()
            rec.state = 'receive'

    # @api.multi
    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.onchange('employee_id')
    def set_department(self):
        for rec in self:
            if rec.employee_id and not rec.employee_id.department_id:
                raise UserError(_("Please set department for %s" % rec.employee_id.name))
            rec.department_id = rec.employee_id.department_id.id
            rec.requisiton_responsible_id = rec.employee_id.parent_id.id
            rec.dest_location_id = rec.employee_id.sudo().dest_location_id.id or rec.employee_id.sudo().department_id.dest_location_id.id
            if rec.dest_location_id:
                internal_picking_type_ids = self.env['stock.picking.type'].search([('code', '=', 'internal'), ('company_id', '=', rec.company_id.id)])
                receipt_picking_type_ids = self.env['stock.picking.type'].search([('code', '=', 'incoming'), ('company_id', '=', rec.company_id.id)])
                for picking in internal_picking_type_ids:
                    rec.custom_picking_type_id = picking.id
                for recepit in receipt_picking_type_ids:
                    rec.custom_receipts_type_id = recepit.id
                rec.location_id = rec.dest_location_id.id

    def show_picking(self):
        for rec in self:
            res = self.env.ref('stock.action_picking_tree_all')
            res = res.read()[0]
            res['domain'] = str([('custom_requisition_id', '=', rec.id)])
            return res

    def action_show_purchase_agreement(self):
        for rec in self:
            purchase_agreement_action = self.env.ref('purchase_requisition.action_purchase_requisition')
            purchase_agreement_action = purchase_agreement_action.read()[0]
            purchase_agreement_action['domain'] = str([('custom_requisition_id', '=', rec.id)])
            return purchase_agreement_action

    @api.depends('employee_id')
    # @api.onchange('employee_id')
    def _check_ami_responsible(self):
        res = self.env['res.users'].browse(self.env.uid)
        print(res.id)
        for rec in self:
            if rec.create_uid.id == res.id and rec.state not in ['draft']:
                rec.is_create = True
            else:
                rec.is_create = False

    @api.depends('employee_id', 'state')
    # @api.onchange('employee_id')
    def _check_is_appear(self):
        for rec in self:
            rec.receive_button_internal = False
            rec.is_appear = False

            if rec.is_create and rec.state in ['internal_transfer']:
                stock_not_done = self.env['stock.picking'].search_count([('custom_requisition_id', '=', rec.id), ('state', '!=', 'done')])
                if stock_not_done > 0:
                    rec.receive_button_internal = False
                else:
                    rec.receive_button_internal = True
            if rec.is_create and rec.state in ['stock']:
                pr = self.env['purchase.requisition'].search([('custom_requisition_id', '=', rec.id)], limit=1)
                pickings = False
                for purchase_req in pr.purchase_ids:
                    if purchase_req.state == 'purchase':
                        pickings = purchase_req.picking_ids.filtered(lambda x: x.state != 'done')
                if pickings:
                    rec.is_appear = False
                else:
                    rec.is_appear = True

    is_create = fields.Boolean(compute="_check_ami_responsible")
    receive_button_internal = fields.Boolean(compute="_check_is_appear")
    is_appear = fields.Boolean(compute="_check_is_appear")

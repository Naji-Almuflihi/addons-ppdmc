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
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.depends('state')
    def _set_purchase_user(self):
        for rec in self:
            if rec.state == 'draft' or 'sent':
                rec.purchase_user_id = self.env.user.id

    @api.model
    def _get_finance_validation_amount(self):
#         finance_validation_amount = self.env['ir.values'].get_default('purchase.config.settings', 'finance_validation_amount')
        finance_validation_amount = self.env.user.company_id.finance_validation_amount
        return finance_validation_amount

    @api.model
    def _get_director_validation_amount(self):
#         director_validation_amount = self.env['ir.values'].get_default('purchase.config.settings', 'director_validation_amount')
        director_validation_amount = self.env.user.company_id.director_validation_amount
        return director_validation_amount

    @api.model
    def _get_three_step_validation(self):
#         three_step_validation = self.env['ir.values'].get_default('purchase.config.settings', 'three_step_validation')
        three_step_validation = self.env.user.company_id.three_step_validation
        return three_step_validation

    @api.model
    def _get_email_template_id(self):
#         email_template_id = self.env['ir.values'].get_default('purchase.config.settings', 'email_template_id')
        email_template_id = self.env.user.company_id.email_template_id
        return email_template_id

    @api.model
    def _get_refuse_template_id(self):
#         refuse_template_id = self.env['ir.values'].get_default('purchase.config.settings', 'refuse_template_id')
        refuse_template_id = self.env.user.company_id.refuse_template_id
        return refuse_template_id

    state = fields.Selection(selection_add=[
        ('budget_approval', 'Waiting Review Budget Approval'),
        ('finance_approval', 'Waiting Finance Approval'),
        ('general_approval', 'Waiting Support Service Approval'),
        ('director_approval', 'Waiting CEO Approval'),
        ('refuse', 'Refuse')],
    )
    po_refuse_user_id = fields.Many2one(
        'res.users',
        string="Refused By",
        readonly = True,
    )
    po_refuse_date = fields.Date(
        string="Refused Date",
        readonly=True
    )
    refuse_reason_note = fields.Text(
        string="Refuse Reason",
        readonly=True
    )
    dept_manager_id = fields.Many2one(
        'res.users',
        string='Purchase Manager',
        states={'done':[('readonly',True)], 'cancel':[('readonly',True)]},
        track_visibility='onchange'
    )
    finance_manager_id = fields.Many2one(
        'res.users',
        string='Finance Manager',
        states={'done':[('readonly',True)], 'cancel':[('readonly',True)]},
        track_visibility='onchange'
    )
    director_manager_id = fields.Many2one(
        'res.users',
        string='CEO',
        states={'done':[('readonly',True)], 'cancel':[('readonly',True)]},
        track_visibility='onchange'
    )
    general_manager_id = fields.Many2one(
        'res.users',
        string='Support Service Manager',
        states={'done':[('readonly',True)], 'cancel':[('readonly',True)]},
        track_visibility='onchange'
    )
    budget_manager_id = fields.Many2one(
        'res.users',
        string='Review Budget Manager',
        states={'done':[('readonly',True)], 'cancel':[('readonly',True)]},
        track_visibility='onchange'
    )
    approve_dept_manager_id = fields.Many2one(
        'res.users',
        string='Approve Purchase Manager',
        readonly=True,
        copy=False,
    )
    approve_finance_manager_id = fields.Many2one(
        'res.users',
        string='Approve Finance Manager',
        readonly=True,
        copy=False,
    )
    approve_general_manager_id = fields.Many2one(
        'res.users',
        string='Approve Support Service Manager',
        readonly=True,
        copy=False,
    )
    approve_budget_manager_id = fields.Many2one(
        'res.users',
        string='Approve Review Budget Manager',
        readonly=True,
        copy=False,
    )
    approve_director_manager_id = fields.Many2one(
        'res.users',
        string='Approve CEO',
        readonly=True,
        copy=False,
    )
    dept_manager_approve_date = fields.Datetime(
        string='Purchase Manager Approve Date',
        readonly=True,
        copy=False,
    )
    finance_manager_approve_date = fields.Datetime(
        string='Finance Manager Approve Date',
        readonly=True,
        copy=False,
    )
    general_manager_approve_date = fields.Datetime(
        string='Support Service Manager Approve Date',
        readonly=True,
        copy=False,
    )
    director_manager_approve_date = fields.Datetime(
        string='CEO Approve Date',
        readonly=True,
        copy=False,
    )
    budget_manager_approve_date = fields.Datetime(
        string='Review Budget Manager Approve Date',
        readonly=True,
        copy=False,
    )
    purchase_user_id = fields.Many2one(
        'res.users',
        string='Purchase User',
        compute='_set_purchase_user',
        store=True,
    )
    budget_status = fields.Selection(selection=[('within_budget', 'Within Budget'), ('finance_approval', 'Without Budget')], string='Budget Status', readonly=True, states={'budget_approval': [('readonly', False), ('required', True)]})

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if 'dept_manager_id' not in fields and 'finance_manager_id' not in fields and 'director_manager_id' not in fields and 'general_manager_id' not in fields and 'budget_manager_id' not in fields:
            return res

        if self.env.user.company_id.three_step_validation:
            if self.env.user.company_id.dept_manager_id:
                res['dept_manager_id'] = self.env.user.company_id.dept_manager_id.id or False

            if self.env.user.company_id.general_manager_id:
                res['general_manager_id'] = self.env.user.company_id.general_manager_id.id or False

            if self.env.user.company_id.finance_manager_id:
                res['finance_manager_id'] = self.env.user.company_id.finance_manager_id.id or False

            if self.env.user.company_id.director_manager_id:
                res['director_manager_id'] = self.env.user.company_id.director_manager_id.id or False

            if self.env.user.company_id.budget_manager_id:
                res['budget_manager_id'] = self.env.user.company_id.budget_manager_id.id or False
        return res

    # def _write(self, vals):
    def write(self, vals):
        for order in self:
            # amount_total = order.currency_id.compute(order.amount_total, order.company_id.currency_id)
            # finance_validation_amount = self._get_director_validation_amount()
            # po_double_validation_amount = self.env.user.company_id.currency_id.compute(order.company_id.po_double_validation_amount, order.currency_id)
            if vals.get('state') == 'to approve':
                if not order.dept_manager_id:
                    raise UserError(_('Please select Purchase Manager.'))
                else:
                    email_to = order.dept_manager_id.partner_id.email
                    email_to_not = order.dept_manager_id.partner_id.id
                    result = self.message_post(
                        body='This Purchase ' + str(
                            order.name) + ' need your approval' + ' click here to open: <a target=_BLANK href="/web?#id=' + str(
                            order.id) + '&view_type=form&model=purchase.order&action=" style="font-weight: bold">' + str(
                            order.name) + '</a>',
                        subtype_xmlid='mail.mt_comment',
                        partner_ids=[email_to_not])

                    email_template_id = self._get_email_template_id()
                    ctx = self._context.copy()
                    ctx.update({'name': order.dept_manager_id.name})
                    # reminder_mail_template.with_context(ctx).send_mail(user)
                    if email_template_id:
                        email_template_id.with_context(ctx).send_mail(self.id, email_values={'email_to': email_to, 'subject': _('Purchase Order: ') + order.name + _(' (Approval Waiting)')})

            if vals.get('state') == 'finance_approval':
                if not order.finance_manager_id:
                    raise UserError(_('Please select Finance Manager.'))
                else:
                    email_to = order.finance_manager_id.partner_id.email
                    email_to_not = order.finance_manager_id.partner_id.id
                    result = self.message_post(
                        body='This Purchase ' + str(
                            order.name) + ' need your approval' + ' click here to open: <a target=_BLANK href="/web?#id=' + str(
                            order.id) + '&view_type=form&model=purchase.order&action=" style="font-weight: bold">' + str(
                            order.name) + '</a>',
                        subtype_xmlid='mail.mt_comment',
                        partner_ids=[email_to_not])

                    email_template_id = self._get_email_template_id()
#                     mail = self.env['mail.template'].browse(email_template_id)
                    ctx = self._context.copy()
                    ctx.update({'name': order.finance_manager_id.name})
                    # mail.send_mail(self.id, email_values={'email_to': email_to, 'subject': "Finance Manager Approve"})
                    if email_template_id:
                        email_template_id.with_context(ctx).send_mail(self.id, email_values={'email_to': email_to, 'subject': _('Purchase Order: ') + order.name + _(' (Approval Waiting)')})

            if vals.get('state') == 'director_approval':
                if not order.director_manager_id:
                    raise UserError(_('Please select CEO.'))
                else:

                    email_to = order.director_manager_id.partner_id.email
                    email_to_not = order.director_manager_id.partner_id.id
                    result = self.message_post(
                        body='This Purchase ' + str(
                            order.name) + ' need your approval' + ' click here to open: <a target=_BLANK href="/web?#id=' + str(
                            order.id) + '&view_type=form&model=purchase.order&action=" style="font-weight: bold">' + str(
                            order.name) + '</a>',
                        subtype_xmlid='mail.mt_comment',
                        partner_ids=[email_to_not])

                    email_template_id = self._get_email_template_id()
#                     mail = self.env['mail.template'].browse(email_template_id)
                    ctx = self._context.copy()
                    ctx.update({'name': order.director_manager_id.name})
                    #mail.send_mail(self.id, email_values={'email_to': email_to, 'subject': "Director Manager Approve"})
                    if email_template_id:
                        email_template_id.with_context(ctx).send_mail(self.id, email_values={'email_to': email_to, 'subject': _('Purchase Order: ') + order.name + _(' (Approval Waiting)')})

            if vals.get('state') == 'general_approval':
                if not order.general_manager_id:
                    raise UserError(_('Please select Support Service Manager.'))
                else:
                    email_to = order.general_manager_id.partner_id.email
                    email_to_not = order.general_manager_id.partner_id.id
                    result = self.message_post(
                        body='This Purchase ' + str(
                            order.name) + ' need your approval' + ' click here to open: <a target=_BLANK href="/web?#id=' + str(
                            order.id) + '&view_type=form&model=purchase.order&action=" style="font-weight: bold">' + str(
                            order.name) + '</a>',
                        subtype_xmlid='mail.mt_comment',
                        partner_ids=[email_to_not])

                    email_template_id = self._get_email_template_id()
#                     mail = self.env['mail.template'].browse(email_template_id)
                    ctx = self._context.copy()
                    ctx.update({'name': order.general_manager_id.name})
                    #mail.send_mail(self.id, email_values={'email_to': email_to, 'subject': "Director Manager Approve"})
                    if email_template_id:
                        email_template_id.with_context(ctx).send_mail(self.id, email_values={'email_to': email_to, 'subject': _('Purchase Order: ') + order.name + _(' (Approval Waiting)')})

            if vals.get('state') == 'budget_approval':
                if not order.budget_manager_id:
                    raise UserError(_('Please select Review Budget Manager.'))
                else:
                    email_to = order.budget_manager_id.partner_id.email
                    email_to_not = order.budget_manager_id.partner_id.id
                    result = self.message_post(
                        body='This Purchase ' + str(
                            order.name) + ' need your approval' + ' click here to open: <a target=_BLANK href="/web?#id=' + str(
                            order.id) + '&view_type=form&model=purchase.order&action=" style="font-weight: bold">' + str(
                            order.name) + '</a>',
                        subtype_xmlid='mail.mt_comment',
                        partner_ids=[email_to_not])

                    email_template_id = self._get_email_template_id()
#                     mail = self.env['mail.template'].browse(email_template_id)
                    ctx = self._context.copy()
                    ctx.update({'name': order.budget_manager_id.name})
                    #mail.send_mail(self.id, email_values={'email_to': email_to, 'subject': "Director Manager Approve"})
                    if email_template_id:
                        email_template_id.with_context(ctx).send_mail(self.id, email_values={'email_to': email_to, 'subject': _('Purchase Order: ') + order.name + _(' (Approval Waiting)')})



            if order.state == 'to approve' and vals.get('state') == 'purchase':
                order.approve_dept_manager_id = self.env.user.id
                order.dept_manager_approve_date = fields.Datetime.now()
            elif order.state == 'to approve' and vals.get('state') == 'budget_approval':
                order.approve_dept_manager_id = self.env.user.id
                order.dept_manager_approve_date = fields.Datetime.now()
            
            if order.state == 'budget_approval' and vals.get('state') == 'purchase':
                order.approve_budget_manager_id = self.env.user.id
                order.budget_manager_approve_date = fields.Datetime.now()
            elif order.state == 'budget_approval' and vals.get('state') == 'finance_approval':
                order.approve_budget_manager_id = self.env.user.id
                order.budget_manager_approve_date = fields.Datetime.now()
            if order.state == 'finance_approval' and vals.get('state') == 'purchase':
                order.approve_finance_manager_id = self.env.user.id
                order.finance_manager_approve_date = fields.Datetime.now()
            elif order.state == 'finance_approval' and vals.get('state') == 'general_approval':
                order.approve_finance_manager_id = self.env.user.id
                order.finance_manager_approve_date = fields.Datetime.now()

            if order.state == 'general_approval' and vals.get('state') == 'purchase':
                order.approve_general_manager_id = self.env.user.id
                order.general_manager_approve_date = fields.Datetime.now()
            elif order.state == 'general_approval' and vals.get('state') == 'director_approval':
                order.approve_general_manager_id = self.env.user.id
                order.general_manager_approve_date = fields.Datetime.now()

            if order.state == 'director_approval' and vals.get('state') == 'purchase':
                order.approve_director_manager_id = self.env.user.id
                order.director_manager_approve_date = fields.Datetime.now()
        return super(PurchaseOrder, self).write(vals)


    def button_budget_approval(self):
        finance_validation_amount = self._get_finance_validation_amount()
        director_validation_amount = self._get_director_validation_amount()
        amount_total = self.currency_id.compute(self.amount_total, self.company_id.currency_id)
        for order in self:
            order.write({'state': 'finance_approval'})
        return True

    def button_finance_approval(self):
        finance_validation_amount = self._get_finance_validation_amount()
        director_validation_amount = self._get_director_validation_amount()
        amount_total = self.currency_id.compute(self.amount_total, self.company_id.currency_id)
        for order in self:
            order.write({'state': 'general_approval'})
        return True

    def button_general_approval(self):
        finance_validation_amount = self._get_finance_validation_amount()
        director_validation_amount = self._get_director_validation_amount()
        amount_total = self.currency_id.compute(self.amount_total, self.company_id.currency_id)
        for order in self:
            if amount_total > director_validation_amount:
                order.write({'state': 'director_approval'})
            if amount_total < director_validation_amount:
                if self.state == 'general_approval':
                    self.name = self.env['ir.sequence'].next_by_code('purchase.order')
                order.button_director_approval()
        return True

    def button_director_approval(self):
        for order in self:
            if self.state == 'director_approval':
                order.write({'state': 'purchase'})
                self.name = self.env['ir.sequence'].next_by_code('purchase.order')
            order.with_context(call_super=True).button_approve()
        return True

    def button_approve(self, force=False):
        if self._context.get('call_super', False):
            return super(PurchaseOrder, self).button_approve(force=force)

        three_step_validation = self._get_three_step_validation()
        if not three_step_validation:
            return super(PurchaseOrder, self).button_approve(force=force)
        amount_total = self.currency_id.compute(self.amount_total, self.company_id.currency_id)
        po_double_validation_amount = self.env.user.company_id.currency_id.compute(self.company_id.po_double_validation_amount, self.currency_id)
        finance_validation_amount = self._get_finance_validation_amount()
        director_validation_amount = self._get_director_validation_amount()
#         if finance_validation_amount > amount_total:
#             return super(PurchaseOrder, self).button_approve()

        if three_step_validation and not self._context.get('call_super', False):
            for order in self:
                if amount_total < director_validation_amount and order.state != 'to approve':
                    order.write({'state': 'to approve'})
                elif order.state == 'to approve':
                    order.state = 'budget_approval'
                elif order.state == 'budget_approval':
                    order.state = 'finance_approval'
                elif order.state == 'finance_approval':
                    order.state = 'general_approval'
                elif order.state == 'draft' and amount_total > director_validation_amount:
                    order.write({'state': 'to approve'})
                else:
                    return super(PurchaseOrder, self).button_approve(force=force)

#                 if order.state == 'to approve':
#                     order.state = 'finance_approval'
#        return True
        return {}


    def action_view_picking(self):
        """ This function returns an action that display existing picking orders of given purchase order ids. When only one found, show the picking immediately.
        """
        result = super(PurchaseOrder, self).action_view_picking()
        if self.env.user.has_group('purchase.group_purchase_manager') or self.env.user.has_group('purchase.group_purchase_user'):
            result['context'] = {'default_partner_id': self.partner_id.id, 'default_origin': self.name,
                                 'default_picking_type_id': self.picking_type_id.id,'create':False,'edit':False}
        else:
            result['context'] = {'default_partner_id': self.partner_id.id, 'default_origin': self.name,
                                 'default_picking_type_id': self.picking_type_id.id}
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    line_number = fields.Integer(string="No",compute="_compute_sequence")

    @api.depends('order_id.order_line', 'order_id.order_line.product_id')
    def _compute_sequence(self):
        for rec in self:
            rec.line_number = 0
            for move in rec:
                count = 0
                if len(move.order_id.order_line) > 1:
                    for mv in move.order_id.order_line:
                        count += 1
                        mv.line_number = count

                if len(move.order_id.order_line) == 1:
                    for mv in move.order_id.order_line:
                        count = 1
                        mv.line_number = count
    
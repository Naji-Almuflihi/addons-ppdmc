# -*- encoding: utf-8 -*-
from datetime import datetime, time
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

DEFAULT_FACTURX_DATE_FORMAT = '%Y%m%d'


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    def _get_picking_in(self):
        pick_in = self.env.ref('stock.picking_type_in', raise_if_not_found=False)
        company = self.env.company
        if not pick_in or pick_in.sudo().warehouse_id.company_id.id != company.id:
            pick_in = self.env['stock.picking.type'].search(
                [('warehouse_id.company_id', '=', company.id), ('code', '=', 'incoming')],
                limit=1,
            )
        return pick_in

    material_picking_type_id = fields.Many2one('stock.picking.type', string='Material Requisition', copy=False)

    def _get_type_id(self):
        return self.env['purchase.requisition.type'].search([], limit=1)

    sequence_id = fields.Many2one('ir.sequence', string="Sequence")
    sequence_next_number = fields.Integer(string="Next Number", compute="_compute_seq_number_next")
    requisition_id = fields.Many2one('purchase.requisition', string='Purchase Agreement', copy=False)
    user_id = fields.Many2one('res.users', string='Purchase Representative', readonly=True, default=lambda self: self.env.user, check_company=True)
    ordering_date = fields.Date(string="Ordering Date", tracking=True, readonly=True)
    type_id = fields.Many2one('purchase.requisition.type', string="Agreement Type", readonly=True,required=True, default=_get_type_id)
    origin = fields.Char(string='Source Document',readonly=True)
    requisition_emp_id = fields.Many2one('hr.employee', string="Purchase Requisition Employee")
    is_requisition_agreement = fields.Boolean(string="")

    @api.constrains('ordering_date', 'schedule_date', 'date_end')
    def _check_dates(self):
        for requisition in self:
            if requisition.schedule_date and requisition.ordering_date and requisition.date_end:
                schedule_date = datetime.strptime(requisition.schedule_date.strftime('%Y%m%d'), '%Y%m%d')
                ordering_date = datetime.strptime(requisition.ordering_date.strftime('%Y%m%d'), '%Y%m%d')
                if requisition.date_end < schedule_date and ordering_date:
                    raise ValidationError(_("Purchase Requisition Agreement Deadline should not be less than Ordering Date and Delivery Date."))

    @api.model
    def create(self, vals):
        res = super(PurchaseRequisition, self).create(vals)
        name = self.env['ir.sequence'].next_by_code('purchase.requisition.seq')
        vals.update({'name': name})

        if not vals.get('sequence_id'):
            vals.update({'sequence_id': self.sudo()._create_sequence(vals).id})

        return res

    def write(self, vals):
        for rec in self:
            if not vals.get('sequence_id'):
                vals.update({'sequence_id': self.sudo()._create_sequence(vals).id})
            else:
                rec.update({'sequence_id': rec.sequence_id.id})
        return super(PurchaseRequisition, self).write(vals)

    @api.model
    def _create_sequence(self, vals, refund=False):

        seq = {
            'name': _('Purchase Requisition Model Sequence'),
            'implementation': 'no_gap',
            'padding': 2,
            'number_increment': 1,
            'use_date_range': True,
        }
        if 'company_id' in vals:
            seq['company_id'] = vals['company_id']
        seq = self.env['ir.sequence'].create(seq)
        seq_date_range = seq._get_current_sequence()
        seq_date_range.number_next = refund and vals.get('refund_sequence_number_next', 1) or vals.get('sequence_number_next', 1)
        return seq

    @api.depends('sequence_id.use_date_range', 'sequence_id.number_next_actual')
    def _compute_seq_number_next(self):
        '''Compute 'sequence_number_next' according to the current sequence in use,
        an ir.sequence or an ir.sequence.date_range.
        '''
        for rec in self:
            if rec.sequence_id:
                sequence = rec.sequence_id._get_current_sequence()
                rec.sequence_next_number = sequence.number_next_actual
            else:
                rec.sequence_next_number = 1

    def action_in_progress(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_("You cannot confirm agreement '%s' because there is no product line.", self.name))
        if self.type_id.quantity_copy == 'none' and self.vendor_id:
            for requisition_line in self.line_ids:
                if requisition_line.price_unit <= 0.0:
                    raise UserError(_('You cannot confirm the blanket order without price.'))
                if requisition_line.product_qty <= 0.0:
                    raise UserError(_('You cannot confirm the blanket order without quantity.'))
                requisition_line.create_supplier_info()
            self.write({'state': 'ongoing'})
        else:
            self.write({'state': 'in_progress'})
        # Set the sequence number regarding the requisition type
        if self.name == 'New':
            if self.is_quantity_copy != 'none':
                self.name = self.env['ir.sequence'].next_by_code('purchase.requisition.tender.extend')
            else:
                self.name = self.env['ir.sequence'].next_by_code('purchase.requisition.blanket.order')


class NewModule(models.Model):
    _inherit = 'purchase.requisition.line'

    is_requisition_agreement = fields.Boolean(string="", related="requisition_id.is_requisition_agreement" )



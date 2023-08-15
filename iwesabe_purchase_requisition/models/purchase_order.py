# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _default_picking_type(self):
        return self._get_picking_type(self.env.context.get('company_id') or self.env.company.id)

    def _get_picking_type(self, company_id):
        for rec in self:
            picking_type = self.env['stock.picking.type'].search(
                [('id', '=',rec.requisition_id.material_picking_type_id.id )])
            picking_type_id = self.env['stock.picking.type'].search(
                [('id', '=', rec.requisition_id.picking_type_id.id)])
            if rec.requisition_id.material_picking_type_id or rec.requisition_id.picking_type_id:
                return picking_type[:1].id or picking_type_id[:1].id
            else:
                picking_type = self.env['stock.picking.type'].search(
                    [('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)])
                if not picking_type:
                    picking_type = self.env['stock.picking.type'].search(
                        [('code', '=', 'incoming'), ('warehouse_id', '=', False)])
                return picking_type[:1]

    requisition_emp_id = fields.Many2one('hr.employee', string="Requisition Employee")
    warning = fields.Char(string="Warning", required=False,compute='check_warning_massage' )

    @api.depends('partner_id','requisition_id')
    def check_warning_massage(self):
        purchase_order_with_same_partner = self.env['purchase.order'].search_count([('partner_id','=',self.partner_id.id),('requisition_id','=',self.requisition_id.id),('id','!=',self._origin.id)])

        if purchase_order_with_same_partner > 0:
            self.warning = 'You are selected this vendor before for the same purchase Agreement'
        else:
            self.warning = False


    @api.model
    @api.onchange('partner_id')
    def onchange_partner_id_warning(self):
        if not self.partner_id:
            return
        warning = {}
        title = False
        message = False
        partner = self.partner_id

        purchase_order_with_same_partner = self.env['purchase.order'].search_count([('partner_id','=',self.partner_id.id),('requisition_id','=',self.requisition_id.id),('id','!=',self._origin.id)])

        if purchase_order_with_same_partner > 0:
            title = ("Warning for %s") % partner.name
            message = 'You are selected this vendor before for the same purchase Agreement'
            warning = {
                'title': title,
                'message': message,
            }

        if warning:
            return {'warning': warning}

    # def button_confirm(self):
    #     res = super(PurchaseOrder,self).button_confirm()
    #     other_rfq = self.env['purchase.order'].search([('id','!=',self.id),('requisition_id','=',self.requisition_id.id)])
    #     for rfq in other_rfq:
    #         rfq.state = 'cancel'
    #     return res

    @api.model
    def create(self, vals):
        company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])
        
        self_comp = self.with_company(company_id)
        if vals.get('name','New') == 'New':
            vals['name'] = '/'
        res = super(PurchaseOrder, self_comp).create(vals)
        
        if res.requisition_id:
            sequence = res.requisition_id.sequence_id
            seq_date = None
            new_name = sequence.with_context(ir_sequence_date=res.date_order.date()).next_by_id()
            if not sequence:
                raise UserError(_('Requisition has no Sequence'))
           
            seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(res.date_order))
            res.name = res.requisition_id.name +'/'+ new_name or '/'
        else:
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
                # res.name = self_comp.env['ir.sequence'].next_by_code('purchase.order', sequence_date=seq_date) or '/'
        for follower in self['message_follower_ids']:
            if follower.id == vals['partner_id']:
                follower.unlink()
        return res


    #todo call super
    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        order_lines = []
        self.order_line.unlink()
        if not self.requisition_id:
            return

        self = self.with_company(self.company_id)
        requisition = self.requisition_id
        self.requisition_emp_id = requisition.requisition_emp_id
        if self.partner_id:
            partner = self.partner_id
        else:
            partner = requisition.vendor_id
        payment_term = partner.property_supplier_payment_term_id

        FiscalPosition = self.env['account.fiscal.position']
        fpos = FiscalPosition.with_company(self.company_id).get_fiscal_position(partner.id)

        self.partner_id = partner.id
        self.fiscal_position_id = fpos.id
        self.payment_term_id = payment_term.id,
        self.company_id = requisition.company_id.id
        self.currency_id = requisition.currency_id.id
        if requisition:
            self.origin = requisition.origin
        self.notes = requisition.description
        self.date_order = fields.Datetime.now()

        if requisition.type_id.line_copy != 'copy':
            return
        if self.requisition_id:
            print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',self.requisition_id.material_picking_type_id.id)
            self.picking_type_id = self.requisition_id.material_picking_type_id.id

        # Create PO lines if necessary
        for line in requisition.line_ids:
            # Compute name
            product_lang = line.product_id.with_context(
                lang=partner.lang,
                partner_id=partner.id
            )
            # name = product_lang.display_name
            name=''
            if product_lang.description_purchase:
                name = product_lang.description_purchase

            # Compute taxes
            taxes_ids = fpos.map_tax(
                line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id)).ids

            # Compute quantity and price_unit
            if line.product_uom_id != line.product_id.uom_po_id:
                product_qty = line.product_uom_id._compute_quantity(line.product_qty, line.product_id.uom_po_id)
                price_unit = line.product_uom_id._compute_price(line.price_unit, line.product_id.uom_po_id)
            else:
                product_qty = line.product_qty
                price_unit = line.price_unit

            if requisition.type_id.quantity_copy != 'copy':
                product_qty = 0

            # Create PO line
            order_line_values = line._prepare_purchase_order_line(
                name=name, product_qty=product_qty, price_unit=price_unit,
                taxes_ids=taxes_ids)
            order_lines.append((0, 0, order_line_values))
            print(">>>>>>>>>>order_lines>>>>>>>>>", order_lines)
        self.order_line = order_lines



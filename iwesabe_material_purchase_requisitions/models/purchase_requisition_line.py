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

from odoo import models, fields, api ,_
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError ,RedirectWarning


class MaterialPurchaseRequisitionLine(models.Model):
    _name = "material.purchase.requisition.line"
    _description = 'Material Purchase Requisition Lines'

    requisition_id = fields.Many2one(
        'material.purchase.requisition',
        string='Requisitions',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
    )
    description = fields.Char(
        string='Description',
        required=True,
    )
    qty = fields.Float(
        string='Quantity',
        # default=1,
        required=True,
    )
    uom = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        required=True,
    )
    partner_id = fields.Many2many(
        'res.partner',
        string='Vendors',
    )
    requisition_type = fields.Selection(
        selection=[
            ('internal', 'Internal Picking'),
            ('purchase', 'Purchase Agreement'),
        ],
        string='Requisition Action',
        default='purchase',
        required=True,
    )
    qty_on_hand = fields.Float(string="QTY Available", compute="get_available_qty", store=False)
    internal_reference = fields.Char(related="product_id.default_code", string="Code")
    line_number = fields.Integer(string="No", compute="_compute_sequence")

    location_id = fields.Many2one(comodel_name="stock.location", string="Source Location", )

    @api.onchange('product_id', 'requisition_type')
    def filter_location(self):
        for rec in self:
            locations_list = []
            quant = self.env['stock.quant'].search([('product_id','=',rec.product_id.id)])
            for q in quant:
                locations_list.append(q.location_id.id)
            return {'domain':{'location_id':[('id','in',locations_list)]}}



    @api.depends('requisition_id.requisition_line_ids', 'requisition_id.requisition_line_ids.product_id')
    def _compute_sequence(self):
        for rec in self:
            rec.line_number = 0
            for move in rec:
                count = 0
                if len(move.requisition_id.requisition_line_ids) > 1:
                    for mv in move.requisition_id.requisition_line_ids:
                        count += 1
                        mv.line_number = count

                if len(move.requisition_id.requisition_line_ids) == 1:
                    for mv in move.requisition_id.requisition_line_ids:
                        count = 1
                        mv.line_number = count

    @api.depends('product_id','location_id')
    def get_available_qty(self):
        for rec in self:
            qty_available = 0.0
            if rec.product_id and rec.location_id:
                for quant in self.sudo().env['stock.quant'].search([('product_id','=',rec.product_id.id),('on_hand', '=', True),('location_id','=',rec.location_id.id)]):
                    qty_available += quant.available_quantity
            rec.qty_on_hand = qty_available

    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            rec.description = rec.product_id.name
            rec.uom = rec.product_id.uom_id.id
            rec.qty_on_hand = rec.product_id.qty_available

    @api.onchange('requisition_type', 'product_id')
    @api.depends('requisition_type', 'product_id')
    def onchange_requisition_type(self):
        b = {}
        for rec in self:
            if rec.requisition_type == 'internal':
                b = {'domain': {'product_id': [('type', 'in', ['product', 'consu'])]}}
            if rec.requisition_type == 'purchase':
                b = {'domain': {'product_id': [('type', 'in', ['product', 'consu'])]}}
            return b

    @api.depends('qty', 'product_id')
    @api.onchange('qty', 'product_id')
    def raise_error_picking_transfer(self):
        for rec in self:
            if rec.requisition_type == "internal" and rec.qty_on_hand < rec.qty:
                raise UserError(_('There is no Quantity for Product to make Internal Transfer'))
            elif rec.requisition_type == "purchase" and rec.qty_on_hand > rec.qty:
                return {'warning':
                    {
                        'title': _("Warning"),
                        'message': 'There is less Quantity than you want'
                    }
                }
            else:
                pass


class HrDepartmentNew(models.Model):
    _inherit = 'hr.department'

    def name_get(self):
        result = []
        for i in self:
            new_name = i.name
            result.append((i.id, "%s" % new_name))
        return result

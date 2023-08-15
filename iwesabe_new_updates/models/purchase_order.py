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
from odoo.exceptions import UserError



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    def confirm_action_new(self):
        products=[]
        lst_rec = []
        requisition = 0
        for rec in self:
            for line in rec.order_line:
                products.append(
                    line.product_id.id,
                )
            requisition = rec.requisition_id.id
            lst_rec.append(rec)
        if len(products) != len(set(products)) :
            raise UserError(
                _('You can not confirm RFQ with same Products.'))
        else:
            for item in lst_rec:
                item.sudo().button_confirm()
        records = self.env['purchase.order'].search([('requisition_id','=',requisition)])
        for r in records:
            if r.state == 'draft':
                r.sudo().update({
                       'state':'cancel'
                   })

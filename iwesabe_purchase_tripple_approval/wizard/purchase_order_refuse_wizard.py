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


class PurchaseOrderRefuseWizard(models.TransientModel):
    _name = 'purchase.order.refuse.wizard'
    _description='refuse'
    
    note = fields.Text(
        string="Refuse Reason",
        required=True,
    )

    #@api.multi
    def action_po_refuse(self):
        purchase_order_id = self.env['purchase.order'].browse(int(self._context.get('active_id')))
        for rec in self:
            purchase_order_id.refuse_reason_note = rec.note
            purchase_order_id.po_refuse_user_id = rec.env.uid
            purchase_order_id.po_refuse_date = fields.date.today()
            refuse_template_id = purchase_order_id._get_refuse_template_id()
#             mail = self.env['mail.template'].browse(refuse_template_id)
            ctx = self._context.copy()

            if purchase_order_id.state == 'to approve':
                ctx.update({
                    'name': purchase_order_id.create_uid.partner_id.name,
                    'email_to': purchase_order_id.create_uid.partner_id.email,
                    'subject': _('Purchase Order: ') + purchase_order_id.name + _(' Refused'),
                    'manager_name': _('Purchase Manager: ') + purchase_order_id.dept_manager_id.name,
                    'reason': rec.note,
                    })
            if purchase_order_id.state == 'finance_approval':
                ctx.update({
                    'name': purchase_order_id.create_uid.partner_id.name,
                    'email_to': purchase_order_id.create_uid.partner_id.email,
                    'subject': _('Purchase Order: ') + purchase_order_id.name + _(' Refused'),
                    'manager_name': _('Finance Manager: ') + purchase_order_id.finance_manager_id.name,
                    'reason': rec.note,
                    })
            if purchase_order_id.state == 'director_approval':
                ctx.update({
                    'name': purchase_order_id.create_uid.partner_id.name,
                    'email_to': purchase_order_id.create_uid.partner_id.email,
                    'subject': _('Purchase Order: ') + purchase_order_id.name + _(' Refused'),
                    'manager_name': _('CEO: ') + purchase_order_id.director_manager_id.name,
                    'reason': rec.note,
                    })
            if refuse_template_id and purchase_order_id.state in ['to approve', 'finance_approval', 'director_approval']:
                refuse_template_id.with_context(ctx).send_mail(purchase_order_id.id)
            purchase_order_id.state = 'refuse'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

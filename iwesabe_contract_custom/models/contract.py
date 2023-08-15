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
from odoo import models, api, fields, _
from datetime import datetime
from dateutil import relativedelta as rd
from odoo.exceptions import UserError, ValidationError


class ContractContract(models.Model):
    _inherit = "contract.contract"

    total_contract = fields.Integer('Total Of Contract', compute="_compute_total_contract", store=True)
    penalty_sheet_id = fields.Many2one('penalty.sheet', string="Penalty Sheet")

    @api.depends('contract_line_fixed_ids', 'date_end', 'date_start', 'recurring_interval', 'recurring_rule_type', 'amount_total')
    def _compute_total_contract(self):
        for rec in self:
            print("GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG")
            rec.total_contract = 0.0
            sub_total = 0.0
            # for rec_line in rec.contract_line_fixed_ids:
            #     sub_total += rec_line.price_subtotal
            # print(sub_total, 'lllllllllllllllllllll')
            if rec.amount_total:
                sub_total = rec.amount_total
            if rec.date_start and rec.date_end:
                dateformat = '%Y-%m-%d'
                startDate = datetime.strptime(str(rec.date_start), dateformat).date()
                endDate = datetime.strptime(str(rec.date_end), dateformat).date()
                r = (endDate - startDate).days
                days = int(r) - 1
                if rec.recurring_interval:
                    if rec.recurring_rule_type == 'daily':
                        rec.total_contract = sub_total * days / rec.recurring_interval
                    elif rec.recurring_rule_type == 'weekly':
                        rec.total_contract = (sub_total * int(int(days / 30) * 4) if type(
                            days / 30) is float else 4) / rec.recurring_interval
                    elif rec.recurring_rule_type == 'monthly':
                        rec.total_contract = (sub_total * int(days / 30)) / rec.recurring_interval
                    elif rec.recurring_rule_type == 'monthlylastday':
                        rec.total_contract = (sub_total * int(days / 30)) / rec.recurring_interval
                    elif rec.recurring_rule_type == 'quarterly':
                        rec.total_contract = (sub_total * int(int(days / 364) * 4) if type(
                            days / 365) is float else 4) / rec.recurring_interval
                    elif rec.recurring_rule_type == 'semesterly':
                        rec.total_contract = (sub_total * int(int(days / 364) * 6) if type(
                            days / 365) is float else 6) / rec.recurring_interval
                    else:
                        rec.total_contract = (sub_total * int(days / 364)) / rec.recurring_interval

    def recurring_create_invoice(self):
        """
        This method triggers the creation of the next invoices of the contracts
        even if their next invoicing date is in the future.
        """
        invoice = self._recurring_create_invoice()
        if invoice:
            self.message_post(
                body=_(
                    "Contract manually invoiced: "
                    '<a href="#" data-oe-model="%s" data-oe-id="%s">Invoice'
                    "</a>"
                )
                % (invoice._name, invoice.id)
            )
        if self.contract_penalty_line_ids:
            users_ids = self.contract_penalty_line_ids.mapped("responsible_id")
            pen_sheet = self.env['penalty.sheet']
            pen_sheet_lines = self.env['penalty.sheet.lines']
            for usr in users_ids:
                # pen_total = 0.0
                pen_data = {'responsible_id': usr.id, 'contract_id': self.id, 'move_id': invoice.id}
                sheet_id = pen_sheet.create(pen_data)
                for pen in self.contract_penalty_line_ids:
                    if pen.responsible_id.id == usr.id:
                        pen_sheet_lines.create({'item_id': pen.position_description_id.id, 'sheet_id': sheet_id.id})
                # sheet_id.write({'penalty_total': pen_total})

                self.write({'penalty_sheet_id': sheet_id.id})
                self.message_post(body='This Penalty ' + str(sheet_id.name) + ' is Created For You' + ' From This Contract ' + str(self.name) + ' click here to open: <a target=_BLANK href="/web?#id=' +
                                  str(sheet_id.id) + '&view_type=form&model=penalty.sheet&action=" style="font-weight: bold">' + str(
                                  sheet_id.name) + '</a>', message_type='comment', subtype_xmlid='mail.mt_comment', partner_ids=[usr.partner_id.id])

                penalty_created_mail_template = self.env.ref('iwesabe_ppmdc_penalty.email_created_penalty_sheet')
                ctx = self._context.copy()
                ctx.update({'email_to': usr.partner_id.email})
                penalty_created_mail_template.with_context(ctx).send_mail(sheet_id.id, force_send=True)
        return invoice

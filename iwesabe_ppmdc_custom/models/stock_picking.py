# -*- coding: utf-8 -*-
from odoo import api, models


class Picking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def get_email_to(self):
        email_list = []
        account_user_group = self.env.ref("account.group_account_user")
        email_list += [usr.partner_id.email for usr in account_user_group.users if usr.partner_id.email]
        return email_list

    def _send_confirmation_email(self):
        super(Picking, self)._send_confirmation_email()
        for stock_pick in self:
            template = self.env.ref('iwesabe_ppmdc_custom.email_send_for_picking_validate')
            assert template._name == 'mail.template'
            email_to_list = self.get_email_to()
            for user in email_to_list:
                template_values = {'email_to': user}
                template.sudo().write(template_values)
                template.sudo().send_mail(stock_pick.id, force_send=True, raise_exception=True)

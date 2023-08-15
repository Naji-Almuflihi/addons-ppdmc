# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Purchase(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        for rec in self:
            template_id = rec.env.ref('iwesabe_new_updates.template_mail_rfq_to_po').id
            template = rec.env['mail.template'].browse(template_id)
            template.send_mail(rec.id, force_send=True)
        return super(Purchase, self).button_confirm()

    @api.model
    def get_email_to(self):
        email_list = []
        user_group = self.env.ref("purchase.group_purchase_user")
        email_list = [
            usr.partner_id.email for usr in user_group.users if
            usr.partner_id.email]
        return ",".join(email_list)

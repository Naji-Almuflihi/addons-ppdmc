""" init object mail.notification """
from odoo import models


class MailNotification(models.Model):
    """init object mail.notification"""
    _inherit = 'mail.notification'

    def write(self, vals):
        """ Override write to fix notification"""
        if vals.get('email_status') == 'ready' and vals.get(
                'is_email') and vals.get('is_read'):
            vals['is_read'] = False
        return super(MailNotification, self).write(vals)

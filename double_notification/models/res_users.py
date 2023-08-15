""" init object res.users """
from odoo import fields, models


class ResUsers(models.Model):
    """ init object  res.users """
    _inherit = 'res.users'

    # notification_type = fields.Selection(
    #     selection_add=[('inbox_with_email',
    #                     'Double Notification Inbox With Email')],
    # )
    notification_type = fields.Selection([
        ('email', 'Handle by Emails'),
        ('inbox', 'Handle in Odoo'),('inbox_with_email',
                        'Double Notification Inbox With Email')],
        'Notification', required=True, default='email',
        help="Policy on how to handle Chatter notifications:\n"
             "- Handle by Emails: notifications are sent to your email address\n"
             "- Handle in Odoo: notifications appear in your Odoo Inbox")
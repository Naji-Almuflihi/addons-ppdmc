""" Test Mail Message """
from odoo.tests.common import TransactionCase
from odoo import _


class TestMailMessage(TransactionCase):
    """Integrated Tests"""

    def setUp(self):
        """Setup the testing environment."""
        super(TestMailMessage, self).setUp()
        self.admin_partner = self.env.ref('base.partner_admin')
        self.demo_partner = self.env.ref('base.partner_demo')
        self.msg = self.env['mail.message'].create({
            'subject': 'Inquiry',
            'model': 'res.partner',
            'author_id': self.admin_partner.id,
            'email_from': 'jdunagan@leclub.example.com',
            'message_type': 'email',
        })
        self.demo_partner.user_ids[0].notification_type = 'inbox_with_email'

    # pylint: disable=protected-access
    def test_notify_mail_message(self):
        """ Test Scenario: test notify mail message"""
        result = self.env['res.partner'].create({'name': 'test partner'})
        result = result.message_post(
            body=_('Test'), message_type='comment', subtype='mail.mt_comment',
            partner_ids=[self.admin_partner.id])
        self.assertTrue(result)
        self.assertTrue(result.notification_ids[0].is_read)

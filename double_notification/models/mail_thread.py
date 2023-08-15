""" init object mail.message """
from odoo import models


class MailThread(models.AbstractModel):
    """ init object mail.message """
    _inherit = 'mail.thread'

    # pylint: disable=no-member, too-many-branches, too-many-locals
    def _notify_compute_recipients(self, message, msg_vals):
        """
        Replace This Function to add Double Notification Inbox With Email.
        ------------------------------------------------------------------
        Compute recipients to notify based on subtype and followers. This
        method returns data structured as expected for ``_notify_recipients``.
        """
        msg_sudo = self.sudo()
        pids = msg_vals.get('partner_ids', []) \
            if msg_vals else msg_sudo.partner_ids.ids
        cids = msg_vals.get('channel_ids', []) \
            if msg_vals else msg_sudo.channel_ids.ids
        message_type = msg_vals.get(
            'message_type') if msg_vals else msg_sudo.message_type
        subtype_id = msg_vals.get('subtype_id') \
            if 'subtype_id' in msg_vals else msg_sudo.subtype_id.id
        recipient_data = {
            'partners': [],
            'channels': [],
        }
        # pylint: disable=protected-access
        res = self.env['mail.followers'].\
            _get_recipient_data(self, message_type, subtype_id, pids, cids)
        if not res:
            return recipient_data
        author_id = msg_vals.get('author_id') or message.author_id.id

        for pid, cid, active, pshare, ctype, notif, groups in res:
            if pid and pid == author_id and not self.env.context.get(
                    'mail_notify_author'):
                continue
            if pid:
                if active is False:
                    # avoid to notify inactive partner by email (odoobot)
                    continue
                pdata = {'id': pid, 'active': active, 'share': pshare,
                         'groups': groups}
                if notif == 'inbox':
                    recipient_data['partners'].append(
                        dict(pdata, notif=notif, type='user'))
                elif notif == 'email':
                    if not pshare and notif:
                        recipient_data['partners'].append(
                            dict(pdata, notif='email', type='user'))
                    elif pshare and notif:
                        recipient_data['partners'].append(
                            dict(pdata, notif='email', type='portal'))
                    else:
                        recipient_data['partners'].append(
                            dict(pdata, notif='email', type='customer'))
                else:
                    recipient_data['partners'].append(
                        dict(pdata, notif='inbox', type='user'))
                    if not pshare and notif:
                        recipient_data['partners'].append(
                            dict(pdata, notif='email', type='user'))
                    elif pshare and notif:
                        recipient_data['partners'].append(
                            dict(pdata, notif='email', type='portal'))
                    else:
                        recipient_data['partners'].append(
                            dict(pdata, notif='email', type='customer'))
            elif cid:
                if notif in ['inbox', 'email']:
                    recipient_data['channels'].append(
                        {'id': cid, 'notif': notif, 'type': ctype})
                else:
                    recipient_data['channels'].append(
                        {'id': cid, 'notif': 'inbox', 'type': ctype})
                    recipient_data['channels'].append(
                        {'id': cid, 'notif': 'email', 'type': ctype})
        return recipient_data

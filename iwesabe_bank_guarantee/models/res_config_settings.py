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

from odoo import fields, models
from datetime import datetime, date, timedelta


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    guarantee_notification_user_ids = fields.Many2many('res.users',
                                                       related='company_id.guarantee_notification_user_ids',
                                                       readonly=False)
    notification_before = fields.Integer('Notification Before', related='company_id.notification_before',readonly=False)

    def action_guarantee_notification(self):
        now = datetime.now() + timedelta(days=1)
        date_now = now.date()
        guarantee_ids = self.env['bank.guarantee'].search([])
        destination = [x.email for x in self.env.user.company_id.guarantee_notification_user_ids if x.email]
        for guarantee in guarantee_ids:
            if guarantee.renew_date:
                exp_date = guarantee.renew_date - timedelta(days=self.env.user.company_id.notification_before)
                if date_now >= exp_date:
                    template_id = self.env.ref('iwesabe_bank_guarantee.bank_guarantee_email_template')
                    mail_content = "  Hello  " + "<br> Bank Guarantee of " + guarantee.guarantee_number + " is going to expire on " + \
                                   str(guarantee.renew_date) + ". Please renew it before expiry date"
                    if template_id:
                        template_id.email_from = self.company_id.email
                        template_id.email_to = ';'.join(destination)
                        template_id.body_html = mail_content
                        send = template_id.send_mail(self.id, force_send=True)
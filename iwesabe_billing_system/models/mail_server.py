
from odoo import fields,models,api


class IRMailServer(models.Model):
    _inherit = 'ir.mail_server'

    use_in_mail = fields.Boolean(string="Use in send mail")

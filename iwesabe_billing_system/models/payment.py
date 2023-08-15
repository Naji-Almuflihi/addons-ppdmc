from odoo import models, fields


class Payment(models.Model):
    _inherit = 'account.payment'

    bank_grantee_id = fields.Many2one("bank.grantee", string="Bank Grantee Number")
    airline_service_contract_id = fields.Many2one("airline.service.contract",)
    check_bank_grantee = fields.Boolean(string="Bank Grantee")
    is_bank_grantee = fields.Boolean()

    def action_post(self):
        res = super(Payment, self).action_post()
        if self.bank_grantee_id:
            self.bank_grantee_id.state = 'closed'
        return res

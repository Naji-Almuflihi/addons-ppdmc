from odoo import models


class AccountPaymentInherit(models.Model):
    _inherit = 'account.payment'

    def open_partial_payment(self):

        context = {}
        if self.partner_type == 'customer':
            context = {
                'default_partner_type': 'customer',
                'default_payment_type': 'payin',
                'default_partner_id': self.partner_id.id,
                'default_name': self.name,
                'default_move_type': 'out_invoice',
                'default_payment_id': self.id
            }
        elif self.partner_type == 'supplier':
            context = {
                'default_partner_type': 'supplier',
                'default_payment_type': 'payout',
                'default_partner_id': self.partner_id.id,
                'default_name': self.name,
                'default_move_type': 'in_invoice',
                'default_payment_id': self.id
            }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.multi.payment.wizard',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': context,
        }

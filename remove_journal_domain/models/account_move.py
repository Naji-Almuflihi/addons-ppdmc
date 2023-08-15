from odoo import api, models


class Account_MOVE_Inherit(models.Model):

    _inherit = 'account.move'

    @api.depends('company_id', 'invoice_filter_type_domain')
    def _compute_suitable_journal_ids(self):
        for m in self:
            journal_type = m.invoice_filter_type_domain or 'general'
            if m.invoice_filter_type_domain:
                domain = [('company_id', '=', m.company_id.id), ('type', '=', journal_type)]
            else:
                domain = [('company_id', '=', m.company_id.id), ('type', 'in', ['sale', 'purchase', 'general', 'cash', 'bank'])]

            m.suitable_journal_ids = self.env['account.journal'].search(domain)


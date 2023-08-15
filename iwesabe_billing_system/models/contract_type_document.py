from odoo import models, fields


class ContractTypeDocument(models.Model):
    _name = 'contract.type.document'
    _inherit = ['mail.thread']
    _description = "Contact Type Document"

    name = fields.Char(string="Name")
    contract_type = fields.Selection([('bank_grantee', 'Bank Grantee'), ('advance_payments', 'Advance payments'), ('agent_grantee', 'Agent Grantee'), ('without_agent_monthly_invoices', 'without grantee Monthly Invoices')],
                                     string="Payment Grantee options", track_visibility='always', required=True)
    description = fields.Html(string="Description")

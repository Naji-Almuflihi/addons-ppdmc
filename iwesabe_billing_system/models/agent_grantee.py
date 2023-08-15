from odoo import models, fields, api


class AgentGrantee(models.Model):
    _name = 'agent.grantee'
    _inherit = ['mail.thread']

    name = fields.Char(string="Name")
    partner_id = fields.Many2one("res.partner", string="Customer", track_visibility='always')
    agent_grantee_id = fields.Many2one("res.partner", string="Agent Grantee", track_visibility='always', )
    start_date = fields.Date(string="Start Date", track_visibility='always',)
    end_date = fields.Date(string="End Date", track_visibility='always',)
    amount = fields.Float(string="Grantee Amount",  track_visibility='always', )
    state = fields.Selection(string="Status", selection=[('draft', 'Draft'), ('confirmed', 'Confirmed'), ('under_renew', 'Under renew process'), ('canceled', 'Canceled')], default='draft', track_visibility='always')
    airline_service_contract_id = fields.Many2one("airline.service.contract", string="")

    @api.onchange('partner_id')
    def get_agent_grantee(self):
        self.agent_grantee_id = self.partner_id.agent_grantee_id.id

    def confirm_button(self):
        self.state = 'confirmed'

    def renew_button(self):
        self.state = 'under_renew'

    def cancel_button(self):
        self.state = 'canceled'

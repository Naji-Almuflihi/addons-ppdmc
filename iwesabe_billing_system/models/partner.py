from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'

    is_non_airline = fields.Boolean(string="IS Non AIRLINE")
    is_airline = fields.Boolean(string="IS AIRLINE")
    is_gmt_customer = fields.Boolean(string="Is GMT")
    airline_code = fields.Char(string="Airline Code", required=False)
    invoice_peendix_by_mail = fields.Selection(string="Invoice Appendix By Mail", selection=[('pdf', 'PDF'), ('excel', 'Excel'), ], default='pdf')
    agent_grantee_id = fields.Many2one(comodel_name="res.partner", string="Agent Grantee", required=False, track_visibility='always')
    no_of_airline_contract = fields.Integer(string="#contract", compute="get_no_of_contract")

    @api.onchange('is_non_airline', 'is_airline')
    def onchange_is_non_airline(self):
        if self.is_non_airline:
            self.is_airline = False
            self.airline_code = ''
        if self.is_airline:
            self.is_non_airline = False

    def get_no_of_contract(self):
        for res in self:
            res.no_of_airline_contract = 0
            no = self.env['airline.service.contract'].search([('partner_id', '=', res.id)])
            res.no_of_airline_contract = len(no)

    def air_line_service_contract(self):
        self.ensure_one()

        contract_ids = self.env['airline.service.contract'].search([('partner_id', '=', self.id)])
        action = self.env["ir.actions.actions"]._for_xml_id("iwesabe_billing_system.action_airline_services_contract_view")
        if len(contract_ids) > 1:
            action['domain'] = [('id', 'in', contract_ids.ids)]
        elif len(contract_ids) == 1:
            form_view = [(self.env.ref('iwesabe_billing_system.view_airline_services_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = contract_ids.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        return action

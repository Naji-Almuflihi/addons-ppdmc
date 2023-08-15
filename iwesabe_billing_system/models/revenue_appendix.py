from odoo import models, fields, api, _
from odoo.exceptions import UserError


class RevenueAppendix(models.Model):
    _name = "revenue.appendix"
    _description = "Revenue Appendix"

    name = fields.Char(string="Number", default="New")
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    line_ids = fields.One2many('revenue.appendix.line', 'appendix_id', string="Appendix Line")
    appendix_count = fields.Integer(string="#Appendix", compute="get_no_of_invoice", store=True)
    state = fields.Selection([('draft', 'Draft'), ('appendix', 'Appendix'), ('invoice', 'Invoicing'), ('done', 'Done'), ('cancel', 'Cancel')], string="State", default='draft', copy=False)
    revenue_invoice_count = fields.Integer(string="#Invoice other", compute="get_no_of_invoice_revenue")
    invoice_count = fields.Integer(string="#Invoice", compute="get_no_of_invoice_revenue")
    cn_count = fields.Integer(string="#CN", compute="get_no_of_invoice_revenue")

    def get_no_of_invoice_revenue(self):
        acc_obj = self.env['account.move']
        for res in self:
            partner_ids = [par.partner_id.id for par in self.line_ids]
            res.invoice_count = 0.0
            res.revenue_invoice_count = acc_obj.search_count([('revenue_id', '=', res.id), ('appendix_another_customer', '=', False), ('move_type', '=', 'out_invoice'), ('partner_id', 'in', partner_ids)])
            inv_ids = [i.invoice_id.id for i in res.line_ids]
            if len(inv_ids) > 0:
                res.invoice_count = acc_obj.search_count([('appendix_id', 'in', inv_ids), ('appendix_another_customer', '=', False), ('move_type', '=', 'out_invoice'), ('partner_id', 'in', partner_ids)])
            res.cn_count = 0.0
            res.cn_count = acc_obj.search_count([('revenue_id', '=', res.id), ('appendix_another_customer', '=', True), ('move_type', '=', 'out_refund'), ('partner_id', 'in', partner_ids)])

    @api.depends('line_ids', 'line_ids.invoice_id', 'line_ids.is_appendix_created')
    def get_no_of_invoice(self):
        for res in self:
            res.appendix_count = len(res.line_ids.filtered(lambda x: x.invoice_id))

    def action_view_appendix_invoice_new(self):
        invoices = []
        for res in self.line_ids:
            if res.is_appendix_created and res.invoice_id and res.invoice_id.id not in invoices:
                invoices.append(res.invoice_id.id)
        action = self.env["ir.actions.actions"]._for_xml_id("iwesabe_billing_system.action_invoice_appendix_view")
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('iwesabe_billing_system.view_invoice_appendix_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_view_revenue_invoice_new(self):
        invoices = self.env['account.move'].search([('revenue_id', '=', self.id), ('move_type', '=', 'out_invoice')])
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_view_credit_note(self):
        invoices = self.env['account.move'].search([('revenue_id', '=', self.id), ('move_type', '=', 'out_refund')])
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_view_invoice_new(self):
        inv_ids = [i.invoice_id.id for i in self.line_ids]
        if len(inv_ids) == 0:
            action = {'type': 'ir.actions.act_window_close'}
        invoices = self.env['account.move'].search([('appendix_id', 'in', inv_ids), ('appendix_another_customer', '=', False), ('move_type', '=', 'out_invoice')])
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_compute_data(self):
        airport_list = []
        if self.from_date and self.to_date:
            date_domain = [('actual_a_time_date', '>=', self.from_date), ('actual_d_time_date', '<=', self.to_date)]
            ams_data = self.env['ams.data'].search(date_domain)
            for d in ams_data:
                if d.arrival_airline and d.arrival_airline not in airport_list:
                    airport_list.append(d.arrival_airline)
                if d.departure_airline and d.departure_airline not in airport_list:
                    airport_list.append(d.departure_airline)
        partner_list = []
        non_partner_list = []
        if len(airport_list) > 0:
            for air in airport_list:
                partner_id = self.env['res.partner'].search([('airline_code', '=', air), ('is_airline', '=', True)])
                if partner_id and partner_id not in partner_list:
                    partner_list.append(partner_id)
                else:
                    non_partner_list.append(air)     
        if non_partner_list:
            raise UserError(_('please review your customer data and include this %s code', non_partner_list))       
        data_list = []
        if len(partner_list) > 0:
            self.line_ids.unlink()
            for par in partner_list:
                data = {'partner_id': par.id, 'is_appendix_created': False}
                data_list.append((0, 0, data))
            self.line_ids = data_list

    def action_confirm(self):
        self.write({'state': 'appendix'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        for res in self.line_ids:
            if res.invoice_id and res.get_invoice_count() > 0:
                raise UserError(_("You can not Cancel Revenue, Invoice Created for Appendix"))
            if res.term_facilities_utilization or res.system or res.is_400hz or res.ground_handling or res.aircraft_parking_not_registered or res.aircraft_registered or res.plbs_busses or res.security_services or res.bus_transportation:
                raise UserError(_("You can not Cancel Revenue, Invoice Created for Other Customer"))
        self.write({'state': 'cancel'})

    def action_generate_appendix(self):
        for res in self.line_ids:
            if not res.invoice_id and not res.is_canceled:
                res.action_generate_revenue_appendix()

    def unlink(self):
        for res in self:
            if res.state not in ['draft', 'cancel']:
                raise UserError(("You can not delete Done record"))
        return super(RevenueAppendix, self).unlink()

    def create_invoice_for_another_customer(self):
        wiz_id = self.env['invoice.other.customer'].create({})
        inv_list = []
        for res in self.line_ids:
            if res.is_appendix_created and res.invoice_id:
                inv_list.append((0, 0, {'invoice_id': res.invoice_id.id, 'partner_id': res.partner_id.id, 'line_id': res.id}))
        if len(inv_list) > 0:
            wiz_id.invoice_appendix_ids = inv_list
        if wiz_id:
            return {
               'name': _('Appendix Invoice For Other Customer'),
               'res_model': 'invoice.other.customer',
               'type': 'ir.actions.act_window',
               'view_mode': 'form',
               'view_type': 'form',
               'res_id': wiz_id.id,
               'target': 'new',
            }

    def create_invoice_for_airline_customer(self):
        wiz_id = self.env['invoice.customer'].create({})
        inv_list = []
        for res in self.line_ids:
            if res.is_appendix_created and res.invoice_id:
                inv_list.append((0, 0, {'invoice_id': res.invoice_id.id, 'partner_id': res.partner_id.id, 'line_id': res.id}))
        if len(inv_list) > 0:
            wiz_id.invoice_line_ids = inv_list
        if wiz_id:
            return {
               'name': _('Appendix Invoice For Airline Customer'),
               'res_model': 'invoice.customer',
               'type': 'ir.actions.act_window',
               'view_mode': 'form',
               'view_type': 'form',
               'res_id': wiz_id.id,
               'target': 'new',
            }

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('revenue.appendix') or _('New')
        res = super(RevenueAppendix, self).create(vals)
        return res


class RevenueAppendixLine(models.Model):
    _name = 'revenue.appendix.line'
    _description = "Revenue Appendix Line"
    _rec_name = "appendix_id"

    appendix_id = fields.Many2one('revenue.appendix', string="Appendix id")
    partner_id = fields.Many2one('res.partner', string="Partner")
    airline_code = fields.Char(related="partner_id.airline_code", string="Code")
    is_appendix_created = fields.Boolean(string="Appendix Created")
    invoice_id = fields.Many2one('invoice.appendix', string="Appendix Invoice")
    is_canceled = fields.Boolean(string="Is Cancel")
    term_facilities_utilization = fields.Boolean(string="Terminal Facilities Utilization")
    system = fields.Boolean(string="Systems")
    is_400hz = fields.Boolean(string="400Hz")
    ground_handling = fields.Boolean(string="ground_handling")
    aircraft_parking_not_registered = fields.Boolean(string="Aircraft Parking Not Registered")
    aircraft_registered = fields.Boolean(string="Aircraft Registered")
    plbs_busses = fields.Boolean(string="PLB’s & Busses")
    security_services = fields.Boolean(string="Security Services")
    bus_transportation = fields.Boolean(string="Buss Transportation")
    state = fields.Selection(related="appendix_id.state", store=True)
    from_date = fields.Date(related="appendix_id.from_date", string="From Date")
    to_date = fields.Date(related="appendix_id.to_date", string="To Date")

    def check_depens_invoice(self):
        for res in self:
            data = {
                    'is_appendix_created': False,
                    'invoice_id': False,
                    'term_facilities_utilization': False,
                    'system': False,
                    'is_400hz': False,
                    'ground_handling': False,
                    'aircraft_parking_not_registered': False,
                    'aircraft_registered': False,
                    'plbs_busses': False,
                    'security_services': False,
                    'bus_transportation': False}
            res.write(data)

    def action_generate_revenue_appendix(self):
        # check old appendix invoice generated or not

        # if any((a <c) or (a > d)):
        # if any((b < c) or (b > b):
        domain = [
            ('to_date', '>=', self.from_date),
            ('from_date', '<=', self.to_date),
            '|', ('from_date', '>=', self.from_date),
            ('from_date', '<=', self.from_date),
            '|', ('to_date', '>=', self.to_date),
            ('to_date', '<=', self.to_date)
        ]

        old_line_ids = self.env['revenue.appendix.line'].search([('partner_id', '=', self.partner_id.id), ('is_canceled', '=', False), ('id', '!=', self.id)] + domain, limit=1)
        detail = "Appendix  customer"
        for old in old_line_ids:
            detail += "\n"
            detail += "%s -> %s " % (old.appendix_id.name, old.partner_id.name)
        if len(old_line_ids):
            raise UserError(_("You can not create Multiple Appendix Invoice already generated on same time please check " + "\n" + '%s' % detail))
        if self.invoice_id:
            return
        data = {
            'from_date': self.appendix_id.from_date,
            'to_date': self.appendix_id.to_date,
            'partner_id': self.partner_id.id,
            'revenue_id': self.appendix_id.id
        }
        invoice_id = self.env['invoice.appendix'].create(data)
        if invoice_id:
            self.is_canceled = False
            invoice_id.action_compute()
            self.invoice_id = invoice_id.id
            self.is_appendix_created = True
            if self.appendix_id.state == 'draft':
                self.appendix_id.state = 'appendix'

    def action_cancel(self):
        for res in self:
            if res.invoice_id and res.invoice_id.state in ['draft', 'cancel']:
                res.invoice_id.unlink()
            if res.invoice_id and res.invoice_id.state not in ['draft', 'cancel']:
                raise UserError(_("You can not Cancel Revenue, Invoice Created for Appendix and computed"))
            if res.invoice_id and res.get_invoice_count() > 0:
                raise UserError(_("You can not Cancel Revenue, Invoice Created for Appendix"))
            if res.term_facilities_utilization or res.system or res.is_400hz or res.ground_handling or res.aircraft_parking_not_registered or res.aircraft_registered or res.plbs_busses or res.security_services or res.bus_transportation:
                raise UserError(_("You can not Cancel Revenue, Invoice Created for Other Customer"))
            data = {
                'is_appendix_created': False,
                'invoice_id': False,
                'term_facilities_utilization': False,
                'system': False,
                'is_400hz': False,
                'ground_handling': False,
                'aircraft_parking_not_registered': False,
                'aircraft_registered': False,
                'plbs_busses': False,
                'security_services': False,
                'bus_transportation': False,
                'is_canceled': True
            }
            res.write(data)

    def get_invoice_count(self):
        invoice_count = 0
        invoice_count = self.env['account.move'].search_count([('appendix_id', '=', self.invoice_id.id), ('appendix_another_customer', '=', False), ('move_type', '=', 'out_invoice'), ('partner_id', '=', self.partner_id.id)])
        return invoice_count

    def action_view_invoice_from_appendx(self):
        if not self.invoice_id:
            action = {'type': 'ir.actions.act_window_close'}
        invoices = self.env['account.move'].search([('appendix_id', '=', self.invoice_id.id), ('appendix_another_customer', '=', False)])
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def create_invoice_from_appendix(self):
        account_move_obj = self.env['account.move']
        invoice_ids = account_move_obj.search([('appendix_id', '=', self.invoice_id.id), ('appendix_another_customer', '=', False), ('state', '=', 'posted')], limit=2)

        if len(invoice_ids) == 2:
            old_invocie = invoice_ids[1]
            new_invoices = invoice_ids[0]
            diff_amount = old_invocie.amount_total - new_invoices.amount_total

            wiz_id = self.env['invoice.credit.note'].create({'old_invoice_id': old_invocie.id, 'new_invoice_id': new_invoices.id, 'diff_amount': diff_amount, 'appendix_id': self.appendix_id.id, 'applendix_line_id': self.id})
            if wiz_id:
                return {
                   'name': _('Create Invoice/Credit Note for Airline Customer'),
                   'res_model': 'invoice.credit.note',
                   'type': 'ir.actions.act_window',
                   'view_mode': 'form',
                   'view_type': 'form',
                   'res_id': wiz_id.id,
                   'target': 'new',
                }

        else:
            wiz_id = self.env['invoice.customer'].create({})
            inv_list = []
            if self.invoice_id:
                inv_list.append((0, 0, {'invoice_id': self.invoice_id.id, 'partner_id': self.partner_id.id, 'line_id': self.id}))
            if len(inv_list) > 0:
                wiz_id.invoice_line_ids = inv_list
            if wiz_id:
                return {
                   'name': _('Appendix Invoice For Airline Customer'),
                   'res_model': 'invoice.customer',
                   'type': 'ir.actions.act_window',
                   'view_mode': 'form',
                   'view_type': 'form',
                   'res_id': wiz_id.id,
                   'target': 'new',
                }

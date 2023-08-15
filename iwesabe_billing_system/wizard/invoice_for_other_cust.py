# See LICENSE file for full copyright and licensing details

from odoo import models, fields, _
from odoo.exceptions import UserError


class InvoiceForOtherCustomer(models.TransientModel):
    _name = 'invoice.other.customer'
    _description = 'Invoice For Other Customer'

    invoice_appendix_ids = fields.One2many('invoice.other.customer.line', 'other_cust_wiz_id', string="Invoice")
    partner_id = fields.Many2one('res.partner', string="Partner")
    term_facilities_utilization = fields.Boolean(string="Terminal Facilities Utilization")
    system = fields.Boolean(string="Systems")
    is_400hz = fields.Boolean(string="400Hz")
    ground_handling = fields.Boolean(string="ground_handling")
    aircraft_parking_not_registered = fields.Boolean(string="Aircraft Parking Not Registered")
    aircraft_registered = fields.Boolean(string="Aircraft Registered")
    plbs_busses = fields.Boolean(string="PLB’s & Busses")
    security_services = fields.Boolean(string="Security Services")
    bus_transportation = fields.Boolean(string="Buss Transportation")

    def create_invoice(self):
        account_inv_obj = self.env['account.move']
        pricing = self.env['billing.pricing']
        invoice_lines = []
        revenue_id = False
        for inv in self.invoice_appendix_ids:
            inv_id = inv.line_id
            revenue_id = inv.line_id.appendix_id
            invoice_appendix_line_ids = inv.invoice_id.invoice_appendix_line_ids
            term_facilities_utilization = systems = field_400_hz = ground_handling = aircraft_parking_not_registered = False
            plb_busses = security_services = bus_transportation = aircraft_registered = False

            if self.term_facilities_utilization and not inv_id.term_facilities_utilization:
                term_facilities_utilization = pricing.search([('type', '=', 'term_facilities_utilization'), ('allow_other_customer', '=', True)], limit=1).product_id
                if term_facilities_utilization:
                    if term_facilities_utilization.property_account_income_id:
                        term_facilities_utilization_account = term_facilities_utilization.property_account_income_id.id
                    elif term_facilities_utilization.categ_id.property_account_income_categ_id:
                        term_facilities_utilization_account = term_facilities_utilization.categ_id.property_account_income_categ_id.id
                    else:
                        raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                        % (term_facilities_utilization.name, term_facilities_utilization.id))
                    term_facilities_price = sum(invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('term_facilities_utilization'))
                    if term_facilities_price > 0:
                        invoice_lines.append({
                            'name': term_facilities_utilization.name + str(' With Tax'),
                            'product_id': term_facilities_utilization.id,
                            'tax_ids': term_facilities_utilization.taxes_id.ids,
                            'account_id': term_facilities_utilization_account,
                            'price_unit': term_facilities_price
                        })
                    term_facilities_price_without_vat = sum(invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('term_facilities_utilization'))
                    if term_facilities_price_without_vat > 0:
                        invoice_lines.append({
                            'name': term_facilities_utilization.name,
                            'product_id': term_facilities_utilization.id,
                            'account_id': term_facilities_utilization_account,
                            'price_unit': term_facilities_price_without_vat
                        })
                    inv_id.term_facilities_utilization = True

            if self.system and not inv_id.system:
                systems = pricing.search([('type', '=', 'systems'), ('allow_other_customer', '=', True)], limit=1).product_id
                if systems:
                    if systems.property_account_income_id:
                        systems_account = systems.property_account_income_id.id
                    elif systems.categ_id.property_account_income_categ_id:
                        systems_account = systems.categ_id.property_account_income_categ_id.id
                    else:
                        raise UserError(_('Please define income account for this Service: "%s" (id:%d).') % (systems.name, systems.id))
                    systems_price = sum(invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('systems'))
                    if systems_price > 0:
                        invoice_lines.append({
                            'name': systems.name + str(' With Tax'),
                            'product_id': systems.id,
                            'tax_ids': systems.taxes_id.ids,
                            'account_id': systems_account,
                            'price_unit': systems_price
                        })
                    systems_price_without_vat = sum(invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('systems'))
                    if systems_price_without_vat > 0:
                        invoice_lines.append({
                            'name': systems.name,
                            'product_id': systems.id,
                            'account_id': systems_account,
                            'price_unit': systems_price_without_vat
                        })
                    inv_id.system = True

            if self.is_400hz and not inv_id.is_400hz:
                field_400_hz = pricing.search([('type', '=', '400hz'), ('allow_other_customer', '=', True)], limit=1).product_id
                if field_400_hz:
                    if field_400_hz.property_account_income_id:
                        field_400_hz_incom_account = field_400_hz.property_account_income_id.id
                    elif systems.categ_id.property_account_income_categ_id:
                        field_400_hz_incom_account = field_400_hz.categ_id.property_account_income_categ_id.id
                    else:
                        raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                        % (field_400_hz.name, field_400_hz.id))
                    field_400_hz_price = sum(invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('field_400_hz'))
                    if field_400_hz_price > 0:
                        invoice_lines.append({
                            'name': field_400_hz.name + str(' With Tax'),
                            'product_id': field_400_hz.id,
                            'tax_ids': field_400_hz.taxes_id.ids,
                            'account_id': field_400_hz_incom_account,
                            'price_unit': field_400_hz_price
                        })
                    field_400_hz_price_without_vat = sum(invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('field_400_hz'))
                    if field_400_hz_price_without_vat > 0:
                        invoice_lines.append({
                            'name': field_400_hz.name,
                            'product_id': field_400_hz.id,
                            'account_id': field_400_hz_incom_account,
                            'price_unit': field_400_hz_price_without_vat
                        })
                    inv_id.is_400hz = True

            if self.ground_handling and not inv_id.ground_handling:
                ground_handling = pricing.search([('type', '=', 'ground_handling'), ('allow_other_customer', '=', True)], limit=1).product_id
                if ground_handling:
                    if ground_handling.property_account_income_id:
                        ground_handling_account = ground_handling.property_account_income_id.id
                    elif ground_handling.categ_id.property_account_income_categ_id:
                        ground_handling_account = ground_handling.categ_id.property_account_income_categ_id.id
                    else:
                        raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                        % (ground_handling.name, ground_handling.id))
                    ground_handling_price = sum(invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('ground_handling'))
                    if ground_handling_price > 0:
                        invoice_lines.append({
                            'name': ground_handling.name + str(' With Tax'),
                            'product_id': ground_handling.id,
                            'tax_ids': ground_handling.taxes_id.ids,
                            'account_id': ground_handling_account,
                            'price_unit': ground_handling_price
                        })
                    ground_handling_price_without_tax = sum(invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('ground_handling'))
                    if ground_handling_price_without_tax > 0:
                        invoice_lines.append({
                            'name': ground_handling.name,
                            'product_id': ground_handling.id,
                            'account_id': ground_handling_account,
                            'price_unit': ground_handling_price_without_tax
                        })
                    inv_id.ground_handling = True

            if self.aircraft_parking_not_registered and not inv_id.aircraft_parking_not_registered:
                aircraft_parking_not_registered = pricing.search([('type', '=', 'aircraft_parking_not_registered'), ('allow_other_customer', '=', True)], limit=1).product_id
                if aircraft_parking_not_registered:
                    if aircraft_parking_not_registered.property_account_income_id:
                        aircraft_parking_not_registered_account = aircraft_parking_not_registered.property_account_income_id.id
                    elif aircraft_parking_not_registered.categ_id.property_account_income_categ_id:
                        aircraft_parking_not_registered_account = aircraft_parking_not_registered.categ_id.property_account_income_categ_id.id
                    else:
                        raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                        % (aircraft_parking_not_registered.name, aircraft_parking_not_registered.id))

                    aircraft_parking_not_registered_price = sum(invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('aircraft_parking_not_registered'))
                    if aircraft_parking_not_registered_price > 0:
                        invoice_lines.append({
                            'name': aircraft_parking_not_registered.name + str(' With Tax'),
                            'product_id': aircraft_parking_not_registered.id,
                            'tax_ids': aircraft_parking_not_registered.taxes_id.ids,
                            'account_id': aircraft_parking_not_registered_account,
                            'price_unit': aircraft_parking_not_registered_price
                        })
                    aircraft_parking_not_registered_price_without_tax = sum(invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('aircraft_parking_not_registered'))
                    if aircraft_parking_not_registered_price_without_tax > 0:
                        invoice_lines.append({
                            'name': aircraft_parking_not_registered.name,
                            'product_id': aircraft_parking_not_registered.id,
                            'account_id': aircraft_parking_not_registered_account,
                            'price_unit': aircraft_parking_not_registered_price_without_tax
                        })
                    inv_id.aircraft_parking_not_registered = True

            if self.aircraft_registered and not inv_id.aircraft_registered:
                aircraft_registered = pricing.search([('type', '=', 'aircraft_registered'), ('allow_other_customer', '=', True)], limit=1).product_id
                if aircraft_registered:
                    if aircraft_registered.property_account_income_id:
                        aircraft_registered_account = aircraft_registered.property_account_income_id.id
                    elif aircraft_registered.categ_id.property_account_income_categ_id:
                        aircraft_registered_account = aircraft_registered.categ_id.property_account_income_categ_id.id
                    else:
                        raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                        % (aircraft_registered.name, aircraft_registered.id))

                    aircraft_registered_price = sum(invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('aircraft_registered'))
                    if aircraft_registered_price > 0:
                        invoice_lines.append({
                            'name': aircraft_registered.name + str(' With Tax'),
                            'product_id': aircraft_registered.id,
                            'tax_ids': aircraft_registered.taxes_id.ids,
                            'account_id': aircraft_registered_account,
                            'price_unit': aircraft_registered_price
                        })
                    aircraft_registered_price_without_tax = sum(invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('aircraft_registered'))
                    if aircraft_registered_price_without_tax > 0:
                        invoice_lines.append({
                            'name': aircraft_registered.name,
                            'product_id': aircraft_registered.id,
                            'account_id': aircraft_registered_account,
                            'price_unit': aircraft_registered_price_without_tax
                        })
                    inv_id.aircraft_registered = True

            if self.plbs_busses and not inv_id.plbs_busses:
                plb_busses = pricing.search([('type', '=', 'PLBs_busses'), ('allow_other_customer', '=', True)], limit=1).product_id
                if plb_busses:
                    if plb_busses.property_account_income_id:
                        plb_busses_account = plb_busses.property_account_income_id.id
                    elif plb_busses.categ_id.property_account_income_categ_id:
                        plb_busses_account = plb_busses.categ_id.property_account_income_categ_id.id
                    else:
                        raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                        % (plb_busses.name, plb_busses.id))
                    plb_busses_price = sum(invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('plb_busses'))
                    if plb_busses_price > 0:
                        invoice_lines.append({
                            'name': plb_busses.name + str(' With Tax'),
                            'product_id': plb_busses.id,
                            'tax_ids': plb_busses.taxes_id.ids,
                            'account_id': plb_busses_account,
                            'price_unit': plb_busses_price
                        })
                    plb_busses_price_without_tax = sum(invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('plb_busses'))
                    if plb_busses_price_without_tax > 0:
                        invoice_lines.append({
                            'name': plb_busses.name,
                            'product_id': plb_busses.id,
                            'account_id': plb_busses_account,
                            'price_unit': plb_busses_price_without_tax
                        })
                    inv_id.plbs_busses = True

            if self.security_services and not inv_id.security_services:
                security_services = pricing.search([('type', '=', 'security_services'), ('allow_other_customer', '=', True)], limit=1).product_id
                if security_services:
                    if security_services.property_account_income_id:
                        security_services_account = security_services.property_account_income_id.id
                    elif security_services.categ_id.property_account_income_categ_id:
                        security_services_account = security_services.categ_id.property_account_income_categ_id.id
                    else:
                        raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                        % (security_services.name, security_services.id))
                    security_services_price = sum(invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('security_services'))
                    if security_services_price > 0:
                        invoice_lines.append({
                            'name': security_services.name + str(' With Tax'),
                            'product_id': security_services.id,
                            'tax_ids': security_services.taxes_id.ids,
                            'account_id': security_services_account,
                            'price_unit': security_services_price
                        })
                    security_services_price_without_tax = sum(invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('security_services'))
                    if security_services_price_without_tax > 0:
                        invoice_lines.append({
                            'name': security_services.name,
                            'product_id': security_services.id,
                            'tax_ids': security_services.taxes_id.ids,
                            'account_id': security_services_account,
                            'price_unit': security_services_price_without_tax
                        })
                    inv_id.security_services = True

            if self.bus_transportation and not inv_id.bus_transportation:
                bus_transportation = pricing.search([('type', '=', 'bus_transportation'), ('allow_other_customer', '=', True)], limit=1).product_id
                if bus_transportation:
                    if bus_transportation.property_account_income_id:
                        bus_transportation_account = bus_transportation.property_account_income_id.id
                    elif bus_transportation.categ_id.property_account_income_categ_id:
                        bus_transportation_account = bus_transportation.categ_id.property_account_income_categ_id.id
                    else:
                        raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                        % (bus_transportation.name, bus_transportation.id))
                    bus_transportation_price = sum(invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('bus_transportation'))
                    if bus_transportation_price > 0:
                        invoice_lines.append({
                            'name': bus_transportation.name + str(' With Tax'),
                            'product_id': bus_transportation.id,
                            'tax_ids': bus_transportation.taxes_id.ids,
                            'account_id': bus_transportation_account,
                            'price_unit': bus_transportation_price
                        })
                    bus_transportation_price_without_tax = sum(invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('bus_transportation'))
                    if bus_transportation_price_without_tax > 0:
                        invoice_lines.append({
                            'name': bus_transportation.name,
                            'product_id': bus_transportation.id,
                            'tax_ids': bus_transportation.taxes_id.ids,
                            'account_id': bus_transportation_account,
                            'price_unit': bus_transportation_price_without_tax
                        })
                    inv_id.bus_transportation = True

        if len(invoice_lines) > 0 and self.partner_id:
            updated_lst = []
            tmp_lst = []
            for up in invoice_lines:
                if up.get('name') not in tmp_lst:
                    tmp_lst.append(up.get('name'))
            for t in tmp_lst:
                price = 0
                new_dct = {}
                for up in invoice_lines:
                    if up.get('name') == t:
                        new_dct = up
                        price += up.get('price_unit')
                        new_dct.update({'price_unit': price})

                updated_lst.append((0, 0, new_dct))

            vals = {
                'move_type': 'out_invoice',
                'appendix_another_customer': True,
                'revenue_id': revenue_id,
                'invoice_date': fields.Date.today(),
                'invoice_date_due': fields.Date.today(),
                'date': fields.Date.today(),
                'customer_contact_id': self.partner_id.child_ids[0] if self.partner_id.child_ids else False,
                'partner_id': self.partner_id.id,
                'invoice_user_id': self.env.user.id,
                'invoice_line_ids': updated_lst,
            }
            invoice_id = account_inv_obj.create(vals)
            if invoice_id and revenue_id:
                revenue_id.write({'state': 'invoice'})
                revenue_id.get_no_of_invoice_revenue()


class InvoiceForOtherCustomerLine(models.TransientModel):
    _name = 'invoice.other.customer.line'

    other_cust_wiz_id = fields.Many2one('invoice.other.customer', string="Other Customer_Invoice")
    invoice_id = fields.Many2one('invoice.appendix', string="Invoice")
    partner_id = fields.Many2one('res.partner', string="Partner")
    line_id = fields.Many2one('revenue.appendix.line', string="Line")

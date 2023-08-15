# See LICENSE file for full copyright and licensing details

from odoo import models, fields, _
from odoo.exceptions import UserError


class InvoiceForCustomer(models.TransientModel):
    _name = 'invoice.customer'
    _description = 'Invoice For Customer'

    appendix_id = fields.Many2one("invoice.appendix", string="Appendix")
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
    invoice_line_ids = fields.One2many('invoice.cutomer.line', 'cust_wiz_id', string="Invoice Ids")

    def create_invoice_multi(self):
        account_inv_obj = self.env['account.move']
        for inv in self.invoice_line_ids:
            invoice_lines = []
            if self.term_facilities_utilization and inv.invoice_id.state == 'confirm':
                invoice_lines += self._prepare_invoice_line_vals_from_pricing(inv.partner_id, inv.invoice_id, 'term_facilities_utilization')
            if self.system and inv.invoice_id.state == 'confirm':
                invoice_lines += self._prepare_invoice_line_vals_from_pricing(inv.partner_id, inv.invoice_id, 'systems')
            if self.is_400hz and inv.invoice_id.state == 'confirm':
                invoice_lines += self._prepare_invoice_line_vals_from_pricing(inv.partner_id, inv.invoice_id, '400hz')
            if self.ground_handling and inv.invoice_id.state == 'confirm':
                invoice_lines += self._prepare_invoice_line_vals_from_pricing(inv.partner_id, inv.invoice_id, 'ground_handling')
            if self.aircraft_parking_not_registered and inv.invoice_id.state == 'confirm':
                invoice_lines += self._prepare_invoice_line_vals_from_pricing(inv.partner_id, inv.invoice_id, 'aircraft_parking_not_registered')
            if self.aircraft_registered and inv.invoice_id.state == 'confirm':
                invoice_lines += self._prepare_invoice_line_vals_from_pricing(inv.partner_id, inv.invoice_id, 'aircraft_registered')
            if self.plbs_busses and inv.invoice_id.state == 'confirm':
                invoice_lines += self._prepare_invoice_line_vals_from_pricing(inv.partner_id, inv.invoice_id, 'PLBs_busses')
            if self.security_services and inv.invoice_id.state == 'confirm':
                invoice_lines += self._prepare_invoice_line_vals_from_pricing(inv.partner_id, inv.invoice_id, 'security_services')
            if self.bus_transportation and inv.invoice_id.state == 'confirm':
                invoice_lines += self._prepare_invoice_line_vals_from_pricing(inv.partner_id, inv.invoice_id, 'bus_transportation')
            if len(invoice_lines) > 0:
                vals = {
                    'appendix_id': inv.invoice_id.id,
                    'move_type': 'out_invoice',
                    'invoice_date': fields.Date.today(),
                    'invoice_date_due': fields.Date.today(),
                    'date': fields.Date.today(),
                    'invoice_origin': inv.invoice_id.name,
                    'customer_contact_id': inv.partner_id.child_ids[0] if inv.partner_id.child_ids else False,
                    'partner_id': inv.partner_id.id,
                    'invoice_user_id': self.env.user.id,
                    'invoice_line_ids': invoice_lines}
                invoice_id = account_inv_obj.create(vals)
                print("invoice id", invoice_id)

    def create_invoice(self):
        account_inv_obj = self.env['account.move']
        for inv in self.invoice_line_ids:
            invoice_lines = []
            if self.term_facilities_utilization:
                invoice_lines += self._prepare_invoice_line_vals_from_pricing(inv.partner_id, inv.invoice_id, 'term_facilities_utilization')
            if self.system:
                invoice_lines += self._prepare_invoice_line_vals_from_pricing(inv.partner_id, inv.invoice_id, 'systems')
            if self.is_400hz:
                invoice_lines += self._prepare_invoice_line_vals_from_pricing(inv.partner_id, inv.invoice_id, '400hz')
            if self.ground_handling:
                invoice_lines += self._prepare_invoice_line_vals_from_pricing(inv.partner_id, inv.invoice_id, 'ground_handling')
            if self.aircraft_parking_not_registered:
                invoice_lines += self._prepare_invoice_line_vals_from_pricing(inv.partner_id, inv.invoice_id, 'aircraft_parking_not_registered')
            if self.aircraft_registered:
                invoice_lines += self._prepare_invoice_line_vals_from_pricing(inv.partner_id, inv.invoice_id, 'aircraft_registered')
            if self.plbs_busses:
                invoice_lines += self._prepare_invoice_line_vals_from_pricing(inv.partner_id, inv.invoice_id, 'PLBs_busses')
            if self.security_services:
                invoice_lines += self._prepare_invoice_line_vals_from_pricing(inv.partner_id, inv.invoice_id, 'security_services')
            if self.bus_transportation:
                invoice_lines += self._prepare_invoice_line_vals_from_pricing(inv.partner_id, inv.invoice_id, 'bus_transportation')
            if len(invoice_lines) > 0:
                vals = {
                    'appendix_id': inv.invoice_id.id,
                    'move_type': 'out_invoice',
                    'invoice_date': fields.Date.today(),
                    'invoice_date_due': fields.Date.today(),
                    'date': fields.Date.today(),
                    'invoice_origin': inv.invoice_id.name,
                    'customer_contact_id': inv.partner_id.child_ids[0] if inv.partner_id.child_ids else False,
                    'partner_id': inv.partner_id.id,
                    'invoice_user_id': self.env.user.id,
                    'invoice_line_ids': invoice_lines}
                invoice_id = account_inv_obj.create(vals)
                print("invoice id", invoice_id)
            else:
                print("no invoice")

    def _prepare_invoice_line_vals_from_pricing(self, partner_id, appendix_id, btype=None):
        if not partner_id or not appendix_id:
            return []
        invoice_lines = []
        invoice_appendix_line_ids = appendix_id.invoice_appendix_line_ids
        if btype:
            billing_pricing_ids = appendix_id.mapped('billing_pricing_ids').filtered(
                lambda b: b.type == btype and not b.allow_other_customer)
        else:
            billing_pricing_ids = appendix_id.mapped('billing_pricing_ids').filtered(
                lambda b: not b.allow_other_customer)
        for pricing in billing_pricing_ids:
            if not pricing.product_id:
                continue
            if not pricing.appendix_line_value_field:
                raise UserError(_("Please configure dynamic fields for (%s)") % pricing.name)
            if pricing.product_id.property_account_income_id:
                pricing_account = pricing.product_id.property_account_income_id.id
            elif pricing.product_id.categ_id.property_account_income_categ_id:
                pricing_account = pricing.product_id.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                % (pricing.product_id.name, pricing.product_id.id))
            price_unit = sum(invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped(
                pricing.appendix_line_value_field.name))
            if price_unit > 0:
                invoice_lines.append((0, 0, {
                    'name': pricing.product_id.name + str(' With Tax'),
                    'product_id': pricing.product_id.id,
                    'tax_ids': pricing.product_id.taxes_id.ids,
                    'account_id': pricing_account,
                    'price_unit': price_unit
                }))
            price_without_vat = sum(invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped(
                pricing.appendix_line_value_field.name))
            if price_without_vat > 0:
                invoice_lines.append((0, 0, {
                    'name': pricing.product_id.name,
                    'product_id': pricing.product_id.id,
                    'account_id': pricing_account,
                    'price_unit': price_without_vat
                }))
        return invoice_lines

    def term_facilities_utilization_function(self, partner_id, appendix_id):
        pricing = self.env['billing.pricing']

        if not partner_id or not appendix_id:
            return []
        invoice_lines = []
        invoice_appendix_line_ids = appendix_id.invoice_appendix_line_ids
        term_facilities_utilization_id = pricing.search(
            [('type', '=', 'term_facilities_utilization'), ('allow_other_customer', '=', False)], limit=1)
        partner_ids = term_facilities_utilization_id.airline_partner_ids.ids
        term_facilities_utilization = term_facilities_utilization_id.product_id

        if term_facilities_utilization and (len(partner_ids) == 0 or partner_id.id in partner_ids):
            if term_facilities_utilization.property_account_income_id:
                term_facilities_utilization_account = term_facilities_utilization.property_account_income_id.id
            elif term_facilities_utilization.categ_id.property_account_income_categ_id:
                term_facilities_utilization_account = term_facilities_utilization.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                % (term_facilities_utilization.name, term_facilities_utilization.id))
            term_facilities_price = sum(
                invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('term_facilities_utilization'))
            if term_facilities_price > 0:
                invoice_lines.append((0, 0, {
                    'name': term_facilities_utilization.name + str(' With Tax'),
                    'product_id': term_facilities_utilization.id,
                    'tax_ids': term_facilities_utilization.taxes_id.ids,
                    'account_id': term_facilities_utilization_account,
                    'price_unit': term_facilities_price
                }))
            term_facilities_price_without_vat = sum(
                invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('term_facilities_utilization'))
            if term_facilities_price_without_vat > 0:
                invoice_lines.append((0, 0, {
                    'name': term_facilities_utilization.name,
                    'product_id': term_facilities_utilization.id,
                    'account_id': term_facilities_utilization_account,
                    'price_unit': term_facilities_price_without_vat
                }))
        return invoice_lines

    def system_function(self, partner_id, appendix_id):
        pricing = self.env['billing.pricing']
        invoice_lines = []
        if not partner_id or not appendix_id:
            return []
        invoice_appendix_line_ids = appendix_id.invoice_appendix_line_ids
        systems_id = pricing.search([('type', '=', 'systems'), ('allow_other_customer', '=', False)], limit=1)
        partner_ids = systems_id.airline_partner_ids.ids
        systems = systems_id.product_id
        if systems and (len(partner_ids) == 0 or partner_id.id in partner_ids):
            if systems.property_account_income_id:
                systems_account = systems.property_account_income_id.id
            elif systems.categ_id.property_account_income_categ_id:
                systems_account = systems.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(
                    _('Please define income account for this Service: "%s" (id:%d).') % (systems.name, systems.id))
            systems_price = sum(invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('systems'))
            if systems_price > 0:
                invoice_lines.append((0, 0, {
                    'name': systems.name + str(' With Tax'),
                    'product_id': systems.id,
                    'tax_ids': systems.taxes_id.ids,
                    'account_id': systems_account,
                    'price_unit': systems_price
                }))
            systems_price_without_vat = sum(
                invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('systems'))
            if systems_price_without_vat > 0:
                invoice_lines.append((0, 0, {
                    'name': systems.name,
                    'product_id': systems.id,
                    'account_id': systems_account,
                    'price_unit': systems_price_without_vat
                }))
        return invoice_lines

    def is_400hz_function(self, partner_id, appendix_id):
        pricing = self.env['billing.pricing']
        invoice_lines = []
        if not partner_id or not appendix_id:
            return []
        invoice_appendix_line_ids = appendix_id.invoice_appendix_line_ids
        field_400_hz_id = pricing.search([('type', '=', '400hz'), ('allow_other_customer', '=', False)], limit=1)
        partner_ids = field_400_hz_id.airline_partner_ids.ids
        field_400_hz = field_400_hz_id.product_id
        if field_400_hz and (len(partner_ids) == 0 or partner_id.id in partner_ids):
            if field_400_hz.property_account_income_id:
                field_400_hz_incom_account = field_400_hz.property_account_income_id.id
            elif field_400_hz.categ_id.property_account_income_categ_id:
                field_400_hz_incom_account = field_400_hz.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                % (field_400_hz.name, field_400_hz.id))
            field_400_hz_price = sum(
                invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('field_400_hz'))
            if field_400_hz_price > 0:
                invoice_lines.append((0, 0, {
                    'name': field_400_hz.name + str(' With Tax'),
                    'product_id': field_400_hz.id,
                    'tax_ids': field_400_hz.taxes_id.ids,
                    'account_id': field_400_hz_incom_account,
                    'price_unit': field_400_hz_price
                }))
            field_400_hz_price_without_vat = sum(
                invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('field_400_hz'))
            if field_400_hz_price_without_vat > 0:
                invoice_lines.append((0, 0, {
                    'name': field_400_hz.name,
                    'product_id': field_400_hz.id,
                    'account_id': field_400_hz_incom_account,
                    'price_unit': field_400_hz_price_without_vat
                }))
        return invoice_lines

    def ground_handling_function(self, partner_id, appendix_id):
        pricing = self.env['billing.pricing']
        invoice_lines = []
        if not partner_id or not appendix_id:
            return []
        invoice_appendix_line_ids = appendix_id.invoice_appendix_line_ids
        ground_handling_id = pricing.search([('type', '=', 'ground_handling'), ('allow_other_customer', '=', False)],
                                            limit=1)
        partner_ids = ground_handling_id.airline_partner_ids.ids
        ground_handling = ground_handling_id.product_id
        if ground_handling and (len(partner_ids) == 0 or partner_id in partner_ids):
            if ground_handling.property_account_income_id:
                ground_handling_account = ground_handling.property_account_income_id.id
            elif ground_handling.categ_id.property_account_income_categ_id:
                ground_handling_account = ground_handling.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                % (ground_handling.name, ground_handling.id))
            ground_handling_price = sum(
                invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('ground_handling'))
            if ground_handling_price > 0:
                invoice_lines.append((0, 0, {
                    'name': ground_handling.name + str(' With Tax'),
                    'product_id': ground_handling.id,
                    'tax_ids': ground_handling.taxes_id.ids,
                    'account_id': ground_handling_account,
                    'price_unit': ground_handling_price
                }))
            ground_handling_price_without_tax = sum(
                invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('ground_handling'))
            if ground_handling_price_without_tax > 0:
                invoice_lines.append((0, 0, {
                    'name': ground_handling.name,
                    'product_id': ground_handling.id,
                    'account_id': ground_handling_account,
                    'price_unit': ground_handling_price_without_tax
                }))

        return invoice_lines

    def aircraft_parking_not_registered_function(self, partner_id, appendix_id):
        pricing = self.env['billing.pricing']
        invoice_lines = []
        if not partner_id or not appendix_id:
            return []
        invoice_appendix_line_ids = appendix_id.invoice_appendix_line_ids
        aircraft_parking_not_registered_id = pricing.search(
            [('type', '=', 'aircraft_parking_not_registered'), ('allow_other_customer', '=', False)], limit=1)
        partner_ids = aircraft_parking_not_registered_id.airline_partner_ids.ids
        aircraft_parking_not_registered = aircraft_parking_not_registered_id.product_id
        if aircraft_parking_not_registered and (len(partner_ids) == 0 or partner_id in partner_ids):
            if aircraft_parking_not_registered.property_account_income_id:
                aircraft_parking_not_registered_account = aircraft_parking_not_registered.property_account_income_id.id
            elif aircraft_parking_not_registered.categ_id.property_account_income_categ_id:
                aircraft_parking_not_registered_account = aircraft_parking_not_registered.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                % (aircraft_parking_not_registered.name, aircraft_parking_not_registered.id))

            aircraft_parking_not_registered_price = sum(
                invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped(
                    'aircraft_parking_not_registered'))
            if aircraft_parking_not_registered_price > 0:
                invoice_lines.append((0, 0, {
                    'name': aircraft_parking_not_registered.name + str(' With Tax'),
                    'product_id': aircraft_parking_not_registered.id,
                    'tax_ids': aircraft_parking_not_registered.taxes_id.ids,
                    'account_id': aircraft_parking_not_registered_account,
                    'price_unit': aircraft_parking_not_registered_price
                }))
            aircraft_parking_not_registered_price_without_tax = sum(
                invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped(
                    'aircraft_parking_not_registered'))
            if aircraft_parking_not_registered_price_without_tax > 0:
                invoice_lines.append((0, 0, {
                    'name': aircraft_parking_not_registered.name,
                    'product_id': aircraft_parking_not_registered.id,
                    'account_id': aircraft_parking_not_registered_account,
                    'price_unit': aircraft_parking_not_registered_price_without_tax
                }))
        return invoice_lines

    def aircraft_registered_function(self, partner_id, appendix_id):
        pricing = self.env['billing.pricing']
        invoice_lines = []
        if not partner_id or not appendix_id:
            return []
        invoice_appendix_line_ids = appendix_id.invoice_appendix_line_ids
        aircraft_registered_id = pricing.search(
            [('type', '=', 'aircraft_registered'), ('allow_other_customer', '=', False)], limit=1)
        partner_ids = aircraft_registered_id.airline_partner_ids.ids
        aircraft_registered = aircraft_registered_id.product_id
        if aircraft_registered and (len(partner_ids) == 0 or partner_id in partner_ids):
            if aircraft_registered.property_account_income_id:
                aircraft_registered_account = aircraft_registered.property_account_income_id.id
            elif aircraft_registered.categ_id.property_account_income_categ_id:
                aircraft_registered_account = aircraft_registered.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                % (aircraft_registered.name, aircraft_registered.id))

            aircraft_registered_price = sum(
                invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('aircraft_registered'))
            if aircraft_registered_price > 0:
                invoice_lines.append((0, 0, {
                    'name': aircraft_registered.name + str(' With Tax'),
                    'product_id': aircraft_registered.id,
                    'tax_ids': aircraft_registered.taxes_id.ids,
                    'account_id': aircraft_registered_account,
                    'price_unit': aircraft_registered_price
                }))
            aircraft_registered_price_without_tax = sum(
                invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('aircraft_registered'))
            if aircraft_registered_price_without_tax > 0:
                invoice_lines.append((0, 0, {
                    'name': aircraft_registered.name,
                    'product_id': aircraft_registered.id,
                    'account_id': aircraft_registered_account,
                    'price_unit': aircraft_registered_price_without_tax
                }))
        return invoice_lines

    def plbs_busses_function(self, partner_id, appendix_id):
        pricing = self.env['billing.pricing']
        invoice_lines = []
        if not partner_id or not appendix_id:
            return []
        invoice_appendix_line_ids = appendix_id.invoice_appendix_line_ids
        plb_busses_id = pricing.search([('type', '=', 'PLBs_busses'), ('allow_other_customer', '=', False)], limit=1)
        partner_ids = plb_busses_id.airline_partner_ids.ids
        plb_busses = plb_busses_id.product_id
        if plb_busses and (len(partner_ids) == 0 or partner_id in partner_ids):
            if plb_busses.property_account_income_id:
                plb_busses_account = plb_busses.property_account_income_id.id
            elif plb_busses.categ_id.property_account_income_categ_id:
                plb_busses_account = plb_busses.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                % (plb_busses.name, plb_busses.id))
            plb_busses_price = sum(invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('plb_busses'))
            if plb_busses_price > 0:
                invoice_lines.append((0, 0, {
                    'name': plb_busses.name + str(' With Tax'),
                    'product_id': plb_busses.id,
                    'tax_ids': plb_busses.taxes_id.ids,
                    'account_id': plb_busses_account,
                    'price_unit': plb_busses_price
                }))
            plb_busses_price_without_tax = sum(
                invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('plb_busses'))
            if plb_busses_price_without_tax > 0:
                invoice_lines.append((0, 0, {
                    'name': plb_busses.name,
                    'product_id': plb_busses.id,
                    'account_id': plb_busses_account,
                    'price_unit': plb_busses_price_without_tax
                }))

        return invoice_lines

    def security_services_function(self, partner_id, appendix_id):
        pricing = self.env['billing.pricing']
        invoice_lines = []
        if not partner_id or not appendix_id:
            return []
        invoice_appendix_line_ids = appendix_id.invoice_appendix_line_ids
        security_services_id = pricing.search(
            [('type', '=', 'security_services'), ('allow_other_customer', '=', False)], limit=1)
        partner_ids = security_services_id.airline_partner_ids.ids
        security_services = security_services_id.product_id
        if security_services and (len(partner_ids) == 0 or partner_id in partner_ids):
            if security_services.property_account_income_id:
                security_services_account = security_services.property_account_income_id.id
            elif security_services.categ_id.property_account_income_categ_id:
                security_services_account = security_services.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                % (security_services.name, security_services.id))
            security_services_price = sum(
                invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('security_services'))
            if security_services_price > 0:
                invoice_lines.append((0, 0, {
                    'name': security_services.name + str(' With Tax'),
                    'product_id': security_services.id,
                    'tax_ids': security_services.taxes_id.ids,
                    'account_id': security_services_account,
                    'price_unit': security_services_price
                }))
            security_services_price_without_tax = sum(
                invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('security_services'))
            if security_services_price_without_tax > 0:
                invoice_lines.append((0, 0, {
                    'name': security_services.name,
                    'product_id': security_services.id,
                    'tax_ids': security_services.taxes_id.ids,
                    'account_id': security_services_account,
                    'price_unit': security_services_price_without_tax
                }))

        return invoice_lines

    def bus_transportation_function(self, partner_id, appendix_id):
        pricing = self.env['billing.pricing']
        invoice_lines = []
        if not partner_id or not appendix_id:
            return []
        invoice_appendix_line_ids = appendix_id.invoice_appendix_line_ids
        bus_transportation_id = pricing.search(
            [('type', '=', 'bus_transportation'), ('allow_other_customer', '=', False)], limit=1)
        partner_ids = bus_transportation_id.airline_partner_ids.ids
        bus_transportation = bus_transportation_id.product_id
        if bus_transportation and (len(partner_ids) == 0 or partner_id in partner_ids):
            if bus_transportation.property_account_income_id:
                bus_transportation_account = bus_transportation.property_account_income_id.id
            elif bus_transportation.categ_id.property_account_income_categ_id:
                bus_transportation_account = bus_transportation.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this Service: "%s" (id:%d).')
                                % (bus_transportation.name, bus_transportation.id))
            bus_transportation_price = sum(
                invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('bus_transportation'))
            if bus_transportation_price > 0:
                invoice_lines.append((0, 0, {
                    'name': bus_transportation.name + str(' With Tax'),
                    'product_id': bus_transportation.id,
                    'tax_ids': bus_transportation.taxes_id.ids,
                    'account_id': bus_transportation_account,
                    'price_unit': bus_transportation_price
                }))
            bus_transportation_price_without_tax = sum(
                invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('bus_transportation'))
            if bus_transportation_price_without_tax > 0:
                invoice_lines.append((0, 0, {
                    'name': bus_transportation.name,
                    'product_id': bus_transportation.id,
                    'tax_ids': bus_transportation.taxes_id.ids,
                    'account_id': bus_transportation_account,
                    'price_unit': bus_transportation_price_without_tax
                }))
        return invoice_lines


class InvoiceForCustomerLine(models.TransientModel):
    _name = 'invoice.cutomer.line'
    _description = "Invoice customer Line"

    cust_wiz_id = fields.Many2one('invoice.customer', string="Customer Invoice")
    invoice_id = fields.Many2one('invoice.appendix', string="Invoice")
    partner_id = fields.Many2one('res.partner', string="Partner")
    line_id = fields.Many2one('revenue.appendix.line', string="Line")

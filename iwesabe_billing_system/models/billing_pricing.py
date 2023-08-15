from odoo import models, fields, api, _
import unicodedata
import re
import random
from odoo.tools import ustr


def sanitize_for_xmlid(s, is_random=False):
    """ Transforms a string to a name suitable for use in an xmlid.
        Strips leading and trailing spaces, converts unicode chars to ascii,
        lowers all chars, replaces spaces with underscores and truncates the
        resulting string to 20 characters.
        :param s: str
        :rtype: str
    """
    s = ustr(s)
    uni = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')

    slug_str = re.sub('[\W]', ' ', uni).strip().lower()
    slug_str = re.sub('[-\s]+', '_', slug_str)
    if is_random:
        return slug_str[:20] + str(random.randint(0, len(s)))
    return slug_str[:20]


class BillingPricing(models.Model):
    _name = 'billing.pricing'
    _rec_name = 'name'

    name = fields.Char(string="Description", required=False)
    type = fields.Selection(string="Service Type",
                            selection=[('term_facilities_utilization', 'Terminal Facilities Utilization'),
                                       ('systems', 'Systems'), ('400hz', '400Hz'), ('ground_handling', 'Ground Handling'),
                                       ('aircraft_parking_not_registered', 'Aircraft Parking Not Registered'),
                                       ('aircraft_registered', 'Aircraft Registered'),
                                       ('PLBs_busses', 'PLB’s & Busses'),
                                       ('security_services', 'Security Services'),
                                       ('bus_transportation', 'Buss Transportation')
                                       ], required=True)
    product_id = fields.Many2one("product.product", string="Service")

    term_facilities_ids = fields.One2many("bill.price.term_facilities", "billing_price_id")
    system_ids = fields.One2many("bill.price.systems", "billing_price_id")
    hz_ids = fields.One2many("bill.price.hz", "billing_price_id")
    ground_handling_ids = fields.One2many("bill.price.ground.handling", "billing_price_id")
    aircraft_not_registered_ids = fields.One2many("bill.price.aircraft.not.registered", "billing_price_id")
    aircraft_registered_ids = fields.One2many("bill.price.aircraft.registered", "billing_price_id")
    blp_buses_ids = fields.One2many("bill.price.blp.buses", "billing_price_id")
    security_services_ids = fields.One2many("bill.price.security.services", "billing_price_id")
    buss_transportation_ids = fields.One2many('bill.price.buss.transportation', 'billing_price_id')
    allow_other_customer = fields.Boolean(string="Non Airline Company")
    # is_ams = fields.Boolean(string="AMS")
    active = fields.Boolean('Active', default=True, help="If unchecked, it will allow you to hide the product without removing it.")
    airline_partner_ids = fields.Many2many('res.partner', 'res_partner_billing_airline_rel', 'partner_id', 'billing_id', string="Partner")
    non_airline_partner_ids = fields.Many2many('res.partner', 'res_partner_billing_non_airline_rel', 'partner_id', 'billing_id', string="Partner")
    # Dynamic Fields
    appendix_line_value_field = fields.Many2one('ir.model.fields', string='Appendix Line Value Field', copy=False)
    appendix_compute_field = fields.Many2one('ir.model.fields', string='Appendix Compute Field', copy=False)
    appendix_total_field = fields.Many2one('ir.model.fields', string='Appendix Total Field', copy=False)
    appendix_line_view_field = fields.Many2one('ir.ui.view', string='Appendix Line View Field',
                                               groups="base.group_system", copy=False)
    sequence = fields.Integer('Sequence', default=16)

    @api.onchange('allow_other_customer')
    def onchange_product_id(self):
        self.airline_partner_ids = False
        self.non_airline_partner_ids = False

    def action_create_dynamic_field(self):
        self.ensure_one()
        if not self.sudo().appendix_line_value_field:
            line_value_field_name = 'x_%s' % (sanitize_for_xmlid(self.name))
            if line_value_field_name in self.env['invoice.appendix.line']._fields:
                line_value_field_name = 'x_%s' % (sanitize_for_xmlid(self.name, is_random=True))
            self.sudo().appendix_line_value_field = self.env['ir.model.fields'].create({
                'name': line_value_field_name,
                'field_description': self.name,
                'model': 'invoice.appendix.line',
                'model_id': self.env.ref('iwesabe_billing_system.model_invoice_appendix_line').id,
                'ttype': 'float',
                'copied': False,
            })
        if not self.sudo().appendix_compute_field:
            compute_field_name = 'x_is_%s' % (sanitize_for_xmlid(self.name))
            if compute_field_name in self.env['invoice.appendix']._fields:
                compute_field_name = 'x_is_%s' % (sanitize_for_xmlid(self.name, is_random=True))
            self.sudo().appendix_compute_field = self.env['ir.model.fields'].create({
                'name': compute_field_name,
                'field_description': '%s %s' % (self.name, 'Compute'),
                'model': 'invoice.appendix',
                'model_id': self.env.ref('iwesabe_billing_system.model_invoice_appendix').id,
                'ttype': 'boolean',
                'copied': False,
            })
        if not self.sudo().appendix_total_field:
            total_field_name = 'x_total_%s' % (sanitize_for_xmlid(self.name))
            if total_field_name in self.env['invoice.appendix']._fields:
                total_field_name = 'x_total_%s' % (sanitize_for_xmlid(self.name, is_random=True))
            self.sudo().appendix_total_field = self.env['ir.model.fields'].create({
                'name': total_field_name,
                'field_description': self.name,
                'model': 'invoice.appendix',
                'model_id': self.env.ref('iwesabe_billing_system.model_invoice_appendix').id,
                'ttype': 'float',
                'copied': False,
            })
        if not self.sudo().appendix_line_view_field:
            inherit_id = self.env.ref('iwesabe_billing_system.view_invoice_appendix_form')
            arch_base = _('<?xml version="1.0"?>\n'
                          '<data>\n'
                          '<field name="%s" position="%s">\n'
                          '<field name="%s" invisible="1"/>\n'
                          '</field>\n'
                          '<xpath expr="//field[@name=\'%s\']//tree//field[@name=\'%s\']" position="%s">\n'
                          '<field name="%s" attrs="{\'column_invisible\': [(\'%s\', \'=\', False)]}" force_save="1" readonly="1" sum="sum"/>\n'
                          '</xpath>\n'
                          '<field name="%s" position="%s">\n'
                          '<field name="%s" attrs="{\'invisible\': [(\'%s\', \'=\', False)]}" force_save="1" readonly="1"/>\n'
                          '</field>\n'
                          '</data>') % (
                "billing_pricing_ids",
                "after",
                self.sudo().appendix_compute_field.name,
                "invoice_appendix_line_ids",
                "fees_total",
                "before",
                self.sudo().appendix_line_value_field.name,
                "parent." + str(self.sudo().appendix_compute_field.name),
                "fees_total_total",
                "before",
                self.sudo().appendix_total_field.name,
                str(self.sudo().appendix_compute_field.name)
            )
            self.sudo().appendix_line_view_field = self.env['ir.ui.view'].sudo().create({
                'name': 'view.invoice.appendix.form.inherit.%s' % self.sudo().appendix_compute_field.name,
                'type': 'form',
                'model': 'invoice.appendix',
                'mode': 'extension',
                'priority': self.sequence,
                'inherit_id': inherit_id.id,
                'arch_base': arch_base,
                'active': True
            })


class BillPriceFiristType(models.Model):
    _name = 'bill.price.term_facilities'

    arrival_passenger_number = fields.Integer(string="Arrival Passenger Price", required=False, )
    departure_passenger_number = fields.Integer(string="Departure Passenger Price", required=False, )
    billing_price_id = fields.Many2one("billing.pricing", string="", required=False, )


class BillPriceSystems(models.Model):
    _name = 'bill.price.systems'

    arrival_passenger_number = fields.Integer(string="Arrival Passenger Price", required=False, )
    departure_passenger_number = fields.Integer(string="Departure Passenger Price", required=False, )
    billing_price_id = fields.Many2one("billing.pricing", string="", required=False, )


class BillPrice400hz(models.Model):
    _name = 'bill.price.hz'

    aircraft_category_id = fields.Many2one("aircraft.category", string="Aircraft Category", required=True, )
    amount = fields.Float(string="Amount",  required=False, )
    billing_price_id = fields.Many2one("billing.pricing", string="", required=False, )


class BillPriceGroundHandling(models.Model):
    _name = 'bill.price.ground.handling'

    aircraft_category_id = fields.Many2one("aircraft.category", string="Aircraft Category", required=True, )
    amount = fields.Float(string="Amount",  required=False, )
    billing_price_id = fields.Many2one("billing.pricing", string="", required=False, )


class BillPriceAircraftNotRegistered(models.Model):
    _name = 'bill.price.aircraft.not.registered'

    from_time = fields.Float(string="From",  required=False, )
    to_time = fields.Float(string="To",  required=False, )
    price = fields.Float(string="Price",  required=False, )

    is_above = fields.Boolean(string="Is Above")

    # first_2_hour = fields.Float(string="Up to 2 Hrs.",  required=False, )
    # more_than_2_to_8_hour = fields.Float(string="Above 2 Hrs. to 8 Hrs.",  required=False, )
    # more_than_8_to_16_hour = fields.Float(string="Above 8 Hrs. to 16 Hrs.",  required=False, )
    # more_than_16_to_24_hour = fields.Float(string="Above 16 Hrs. to 24 Hrs",  required=False, )
    # more_than_24_hour = fields.Float(string="Next & following 24 Hrs.",  required=False, )
    billing_price_id = fields.Many2one("billing.pricing", string="", required=False, )


class BillPriceAircraftRegistered(models.Model):
    _name = 'bill.price.aircraft.registered'

    from_time = fields.Float(string="From", required=False, )
    to_time = fields.Float(string="To", required=False, )
    price = fields.Float(string="Price",  required=False, )
    is_above = fields.Boolean(string="Is Above", )
    billing_price_id = fields.Many2one("billing.pricing", string="", required=False, )


class BillPriceBlpsBuses(models.Model):
    _name = 'bill.price.blp.buses'

    from_ton = fields.Float(string="From ton",  required=False, )
    to_ton = fields.Float(string="To ton",  required=False, )
    price = fields.Float(string="Price",  required=False, )
    is_above = fields.Boolean(string="Is Above", )

    # up_to_50_ton = fields.Float(string="Up to 50 Tons",  required=False, )
    # above_50_to_100_ton = fields.Float(string="Above 50 to 100 Tons",  required=False, )
    # above_100_to_200_ton = fields.Float(string="Above 100 to 200 Tons",  required=False, )
    # above_200_to_300_ton = fields.Float(string="Above 200 to 300 Tons",  required=False, )
    # above_300_to_350_ton = fields.Float(string="Above 300 to 350 Tons",  required=False, )
    # above_350_ton = fields.Float(string="Above 350 Tons",  required=False, )
    billing_price_id = fields.Many2one("billing.pricing", string="", required=False, )


class BillPriceSecurityServices(models.Model):
    _name = 'bill.price.security.services'

    from_ton = fields.Float(string="From ton", required=False, )
    to_ton = fields.Float(string="To ton", required=False, )
    price = fields.Float(string="Price", required=False, )
    is_above = fields.Boolean(string="Is Above", )

    billing_price_id = fields.Many2one("billing.pricing", string="", required=False, )


class BussTransportation(models.Model):
    _name = 'bill.price.buss.transportation'
    _description = "Buss Transportation"

    @api.depends('no_of_flight', 'price_per_flight')
    def get_total_price(self):
        for res in self:
            res.subtotal = 0.0
            if res.no_of_flight and res.price_per_flight:
                res.subtotal = res.no_of_flight * res.price_per_flight

    billing_price_id = fields.Many2one("billing.pricing")
    no_of_flight = fields.Integer(string="No. Of Flight", default=0)
    price_per_flight = fields.Float(string="Price per Flight")
    subtotal = fields.Float(string="Total", compute="get_total_price", store=True)

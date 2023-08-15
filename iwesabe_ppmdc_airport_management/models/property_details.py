# See LICENSE file for full copyright and licensing details


from odoo import _, api, fields, models
from dateutil.relativedelta import relativedelta


class PropertyType(models.Model):
    _name = "property.type"
    _description = "Property Type"

    name = fields.Char(string='Name', required=True)


class RoomType(models.Model):
    _name = "room.type"
    _description = "Room Type"

    name = fields.Char(string='Name', required=True)


class Utility(models.Model):
    _name = "utility"
    _description = "Utility"

    name = fields.Char(string='Name', required=True)


class PlaceType(models.Model):
    _name = 'place.type'
    _description = 'Place Type'

    name = fields.Char(string='Place Type', required=True)


class PropertyPhase(models.Model):
    _name = "property.phase"
    _description = 'Property Phase'
    _rec_name = 'property_id'

    end_date = fields.Date(string='End Date')
    start_date = fields.Date(string='Beginning Date')
    commercial_tax = fields.Float(string='Commercial Tax (in %)')
    occupancy_rate = fields.Float(string='Occupancy Rate (in %)')
    lease_price = fields.Float(string='Sales/lease Price Per Month')
    property_id = fields.Many2one('property.property', string='Property')
    company_income = fields.Float(string='Company Income Tax CIT (in %)')


class PropertyPhoto(models.Model):
    _name = "property.photo"
    _description = 'Property Photo'
    _rec_name = 'doc_name'

    photos = fields.Binary(string='Photos')
    doc_name = fields.Char(string='Filename')
    photos_description = fields.Char(string='Description')
    property_id = fields.Many2one('property.property', string='Property')


class PropertyFloorPhoto(models.Model):
    _name = "property.floor.plans"
    _description = 'Floor Plans'
    _rec_name = 'doc_name'

    photos = fields.Binary(string='Photos')
    doc_name = fields.Char(string='Filename')
    photos_description = fields.Char(string='Description')
    property_id = fields.Many2one('property.property', string='Property')


class NearbyProperty(models.Model):
    _name = 'nearby.property'
    _description = 'Nearby Property'

    distance = fields.Float(string='Distance (Km)')
    name = fields.Char(string='Name')
    type = fields.Many2one('place.type', string='Type')
    property_id = fields.Many2one('property.property', string='Property')


class RoomAssets(models.Model):
    _name = "room.assets"
    _description = "Room Assets"

    date = fields.Date(string='Date')
    name = fields.Char(string='Description')
    type = fields.Selection(
        [('fixed', 'Fixed Assets'),
         ('movable', 'Movable Assets'),
         ('other', 'Other Assets')], string='Type')
    qty = fields.Float(string='Quantity')
    room_id = fields.Many2one('property.room', string='Property')


class PropertyInsurance(models.Model):
    _name = "property.insurance"
    _description = "Property Insurance"

    premium = fields.Float(string='Premium')
    end_date = fields.Date(string='End Date')
    doc_name = fields.Char(string='Filename')
    contract = fields.Binary(string='Contract')
    start_date = fields.Date(string='Start Date')
    name = fields.Char(string='Description')
    policy_no = fields.Char(string='Policy Number')
    contact = fields.Many2one('res.company', string='Insurance Comapny')
    company_id = fields.Many2one('res.company', string='Related Company')
    property_id = fields.Many2one('property.property', string='Property')
    payment_mode_type = fields.Selection(
        [('monthly', 'Monthly'),
         ('semi_annually', 'Semi Annually'),
         ('yearly', 'Annually')], string='Payment Term')


class PropertyUtility(models.Model):
    _name = "property.utility"
    _description = 'Property Utility'

    note = fields.Text(string='Remarks')
    ref = fields.Char(string='Reference')
    expiry_date = fields.Date(string='Expiry Date')
    issue_date = fields.Date(string='Issuance Date')
    utility_id = fields.Many2one('utility', string='Utility')
    property_id = fields.Many2one('property.property', string='Property')
    tenancy_id = fields.Many2one('tenant.tenancy', string='Tenancy')
    contact_id = fields.Many2one('res.partner', string='Contact', domain="[('tenant', '=', True)]")


class PropertySafetyCertificate(models.Model):
    _name = "property.safety.certificate"
    _description = 'Property Safety Certificate'

    ew = fields.Boolean(string='EW')
    weeks = fields.Integer(string='Weeks')
    ref = fields.Char(string='Reference')
    expiry_date = fields.Date(string='Expiry Date')
    name = fields.Char(string='Certificate', required=True)
    property_id = fields.Many2one('property.property', string='Property')
    contact_id = fields.Many2one('res.partner', string='Contact', domain="[('tenant', '=', True)]")


class PropertyAttachment(models.Model):
    _name = 'property.attachment'
    _description = 'Property Attachment'

    doc_name = fields.Char(string='Filename')
    expiry_date = fields.Date(string='Expiry Date')
    contract_attachment = fields.Binary(string='Attachment')
    name = fields.Char(string='Description')
    property_id = fields.Many2one('property.property', string='Property')


class PropertyRentPrice(models.Model):
    _name = 'property.rent.price'
    _description = 'Property Rent Price'

    rent_type_id = fields.Many2one('rent.type', required=True, string='Season Rent')
    year_id = fields.Many2one('season.year', string='Season Year', required=False)
    gfa_meter = fields.Float(string="GFQ(M2)", required=True)
    rent = fields.Float(string="Rent", required=True)
    total = fields.Float(string='Total', compute='_compute_total', store=True)
    property_id = fields.Many2one('property.property', string='Property')

    @api.depends('gfa_meter', 'rent')
    def _compute_total(self):
        for record in self:
            record.total = record.gfa_meter * record.rent


class RentType(models.Model):
    _name = "rent.type"
    _description = "Rent Type"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")
    season_year_ids = fields.One2many('season.year', 'rent_type_id', string="Season Year")
    rent_count = fields.Integer(compute='compute_rent_count')

    @api.depends('name')
    def compute_rent_count(self):
        tenancy_record = self.env['tenant.tenancy'].search([('state', '=', 'open')])
        lines = []
        counter = 0
        for rec in self:
            if tenancy_record:
                for ten in tenancy_record:
                    for line in ten.property_ids:
                        if self.id == line.rent_type_id.id:
                            lines.append(line.id)
                            counter += 1
            rec.rent_count = counter

    def open_property_tenancy(self):
        tenancy_record = self.env['tenant.tenancy'].search([('state', '=', 'open')])
        lines = []
        counter = 0
        if tenancy_record:
            for ten in tenancy_record:
                for line in ten.property_ids:
                    if self.id == line.rent_type_id.id:
                        lines.append(line.id)
                        counter += 1
        self.rent_count = counter

        return {'name': _('Tenancy Contract Expiary'),
                'view_mode': 'tree',
                'view_type': 'form',
                'res_model': 'tenancy.property',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'domain': [('id', 'in', lines)],
                }


class SeasonYear(models.Model):
    _name = 'season.year'
    _description = 'Season Year'

    name = fields.Char(string="Year", required=True)
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    date_from_hijri = fields.Char(string="Date From Hijri")
    date_to_hijri = fields.Char(string="Date To Hijri")
    rent_type_id = fields.Many2one('rent.type', string="Rent Type")
    reminder = fields.Boolean(string="Reminder")
    days_before = fields.Integer(string="Days Before")
    company_id = fields.Many2one('res.company', string='Related Company')

    @api.onchange('date_from')
    def onchange_date_from(self):
        if self.date_from:
            self.with_context({'field_to': 'date_from_hijri', 'field_from': 'date_from'}).Gregorian2hijri()

    @api.onchange('date_to')
    def onchange_date_to(self):
        if self.date_to:
            self.with_context({'field_to': 'date_to_hijri', 'field_from': 'date_to'}).Gregorian2hijri()

    def send_mail_rent_reminder_schedule(self):
        template_id = self.env.ref('iwesabe_ppmdc_airport_management.email_rant_pay_user_reminder')
        for res in self.env['season.year'].search([('reminder', '=', True)]):
            tenancy_record = self.env['tenancy.property'].search([('rent_type_id', '=', res.rent_type_id.id)])
            today = fields.Date.context_today(self) + relativedelta(days=res.days_before or 0)
            if today == res.date_to:
                for tenancy in tenancy_record:
                    if tenancy.partner_id.email:
                        template_id.write({'email_to': tenancy.partner_id.email, 'email_from': self.env.user.company_id.email})
                        template_id.send_mail(res.id, force_send=True)
        return True

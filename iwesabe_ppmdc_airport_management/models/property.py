# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError

from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT




class Property(models.Model):
    _name = 'property.property'
    _description = 'Property'
    _inherit = ['account.asset','mail.thread', 'mail.activity.mixin', 'portal.mixin']


    def _compute_asset_count(self):
        for asset in self:
            res = self.env['account.asset'].search_count(
                [('property_id', '=', asset.id)])
            asset.asset_count = res or 0

    asset_count = fields.Integer(
        string='Assets',
        compute='_compute_asset_count',
        help='Only shows Assets')
    asset_ids = fields.One2many(
        comodel_name='account.asset',
        inverse_name='property_id',
        string='Assets',
        help='Its shows over all maintenance for this property')


    site_id = fields.Many2one(comodel_name="site.site", string="Site")

    def open_assets(self):
        asset = self.env['account.asset'].search([('property_id', '=', self.id)])
        return {
            'name': _('Asset'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.asset',
            'view_id': self.env.ref('account_asset.view_account_asset_form').id,
            'res_id':asset.id,
            'context': {
                'default_name': self.name,
                'default_property_id': self.id
            }
        }

    @api.depends('property_phase_ids', 'property_phase_ids.lease_price')
    def _compute_sales_rates(self):
        """
        This Method is used to calculate total sales rates.
        @param self: The object pointer
        @return: Calculated Sales Rate.
        """
        for prop_rec in self:
            counter = 0
            les_price = 0
            sal_rate = 0
            for phase in prop_rec.property_phase_ids:
                counter += 1
                les_price += phase.lease_price
            if counter != 0 and les_price != 0:
                sal_rate = les_price / counter
            prop_rec.sales_rates = sal_rate

    @api.depends('roi')
    def _compute_ten_year_roi(self):
        """
        This Method is used to Calculate ten years ROI(Return On Investment).
        @param self: The object pointer
        @return: Calculated Return On Investment.
        """
        for rec in self:
            rec.ten_year_roi = 10 * rec.roi



    name = fields.Char(
        string="Name",
        default="/"
    )
    original_move_line_ids = fields.Many2many(
        'account.move.line', 
        'property_move_line_rel', 
        'property_id', 
        'line_id', 
        string='Journal Items', 
        readonly=True, 
        states={'draft': [('readonly', False)]}, 
        copy=False)
    image = fields.Binary(
        "Logo", 
        attachment=True,
        help="This field holds the image used as logo for the brand, limited to 1024x1024px.")
    simulation_date = fields.Date(
        string='Simulation Date',
        help='Simulation Date.')
    township = fields.Char(
        string='Township')
    simulation_name = fields.Char(
        string='Simulation Name')
    construction_cost = fields.Float(
        string='Construction Cost')
    gfa_meter = fields.Float(
        string='GFA(M2)',
        help='Gross floor area in Meter.')
    sale_price = fields.Float(
        string='Sale Price',
        help='Sale price of the Property.')
    sales_rates = fields.Float(
        string="Sales Rate",
        compute='_compute_sales_rates',
        help='Average Sale/Lease price from property phase per Month.')
    ten_year_roi = fields.Float(
        string="10 year ROI",
        compute='_compute_ten_year_roi',
        help="10 year Return of Investment.")
    roi = fields.Float(
        string="ROI",
        store=True,
        help='ROI ( Return On Investment ) = ( Total Tenancy rent - Total \
        maintenance cost ) / Total maintenance cost.', )
    operational_costs = fields.Float(
        string="Operational Costs(%)",
        store=True,
        help='Average of total operational budget and total rent.')
    occupancy_rates = fields.Float(
        string="Occupancy Rate",
        store=True,
        help='Total Occupancy rate of Property.')
    parent_path = fields.Char(index=True)
    simulation = fields.Float(
        string='Total Amount',
        store=True)
    revenue = fields.Float(
        string='Revenue',
        store=True)
    pur_instl_chck = fields.Boolean(
        string='Purchase Installment Check',
        default=False)
    sale_instl_chck = fields.Boolean(
        string='Sale Installment Check',
        default=False)
    color = fields.Integer(
        string='Color',
        default=4)
    floor = fields.Integer(
        string='Floor',
        help='Number of Floors.')
    no_of_property = fields.Integer(
        string='Property Per Floors.',
        help='Number of Properties Per Floor.')
    parent_id = fields.Many2one(
        comodel_name='property.property',
        string='Parent Property')
    maint_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Maintenance Account')
    current_tenant_id = fields.Many2one(
        comodel_name='res.partner',
        string='Current Tenant')
    country_id = fields.Many2one(
        comodel_name='res.country',
        string='Country',
        ondelete='restrict')
    state_id = fields.Many2one(
        comodel_name='res.country.state',
        string='Property State',
        ondelete='restrict')
    property_type_id = fields.Many2one(
        'property.type',
        string='Propert Type',
        required=True
        
    )
    contact_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contact Name',
        domain="[('tenant', '=', True)]")
    property_phase_ids = fields.One2many(
        comodel_name='property.phase',
        inverse_name='property_id',
        string='Phase')
    property_photo_ids = fields.One2many(
        comodel_name='property.photo',
        inverse_name='property_id',
        string='Photos')
    floor_plans_ids = fields.One2many(
        comodel_name='property.floor.plans',
        inverse_name='property_id',
        string='Floor Plans ')
    utility_ids = fields.One2many(
        comodel_name='property.utility',
        inverse_name='property_id',
        string='Utilities')
    nearby_ids = fields.One2many(
        comodel_name='nearby.property',
        inverse_name='property_id',
        string='Nearest Property')
    contract_attachment_ids = fields.One2many(
        comodel_name='property.attachment',
        inverse_name='property_id',
        string='Document')
    child_ids = fields.One2many(
        comodel_name='property.property',
        inverse_name='parent_id',
        string='Children Property')
    property_insurance_ids = fields.One2many(
        comodel_name='property.insurance',
        inverse_name='property_id',
        string='Insurance')
    safety_certificate_ids = fields.One2many(
        comodel_name='property.safety.certificate',
        inverse_name='property_id',
        string='Safety Certificate')
    account_move_ids = fields.One2many(
        comodel_name='account.move',
        inverse_name='asset_id',
        string='Entries',
        readonly=True,
        states={'draft': [('readonly', False)]})
    bedroom = fields.Selection(
        [('1', '1'), ('2', '2'),
         ('3', '3'), ('4', '4'),
         ('5', '5+')],
        string='Bedrooms',
        default='1')
    bathroom = fields.Selection(
        [('1', '1'), ('2', '2'),
         ('3', '3'), ('4', '4'),
         ('5', '5+')],
        string='Bathrooms',
        default='1')
    parking = fields.Selection(
        [('1', '1'), ('2', '2'),
         ('3', '3'), ('4', '4'),
         ('5', '5+')],
        string='Parking',
        default='1')
    facing = fields.Selection(
        [('north', 'North'), ('south', 'South'),
         ('east', 'East'), ('west', 'West')],
        string='Facing',
        default='east')
    furnished = fields.Selection(
        [('none', 'None'),
         ('semi_furnished', 'Semi Furnished'),
         ('full_furnished', 'Full Furnished')],
        string='Furnishing',
        default='none',
        help='Furnishing.')
    state = fields.Selection(
        [
            ('new_draft', 'Booking Open'),
            ('draft', 'Available'),
            ('book', 'Booked'),
            ('normal', 'On Lease'),
            ('close', 'Sale'),
            ('sold', 'Sold'),
            ('open', 'Running'),
            ('cancel', 'Cancel')],
        string='State', default='draft')
    # latitude = fields.Float(
    #     string='Latitude',
    #     digits=(16, 8),
    #     help='Latitude of the place.')
    # longitude = fields.Float(
    #     string='Longitude',
    #     digits=(16, 8),
    #     help='Longitude of the place.')
    note = fields.Text(
        string="Notes")
    room_id = fields.Many2one(
        'property.room',
        string="Room Number"
    )
    zone_id = fields.Many2one(
        'property.zone',
        string="Module"
    )

    zone_number_number_id = fields.Many2one(
        'property.zone.number.number',
        string="Zone Number"
    )

    live_id = fields.Many2one(
        'property.live',
        string="Level Number"
    )
    rent_price_ids = fields.One2many(
        'property.rent.price',
        'property_id',
        string="Rent Price"
    )
    zone_number_id = fields.Many2one(
          'property.zone.number',
          string='Zone Number',
     )

    is_sub_property = fields.Boolean()
    sub_sequence = fields.Char()
    check_same_property = fields.Boolean()

    @api.onchange('zone_id', 'room_id', 'zone_number_number_id', 'live_id', 'sub_sequence')
    def compute_property_name(self):
        if self.live_id and self.zone_id and self.zone_number_number_id and self.room_id and not self.sub_sequence:
            self.name = str(self.live_id.name) + '-' + str(self.zone_id.name)+str(self.zone_number_number_id.name) + '-' + str(self.room_id.name)
        elif self.live_id and self.zone_id and self.zone_number_number_id and self.room_id and self.sub_sequence:
            self.name = str(self.sub_sequence)+'-'+str(self.live_id.name) + '-' + str(self.zone_id.name)+str(self.zone_number_number_id.name) + '-' + str(self.room_id.name)
        for rec in self.search([
            ('zone_id','=',self.zone_id.id),
            ('room_id','=',self.room_id.id),
            ('zone_number_number_id','=',self.zone_number_number_id.id),
            ('live_id','=',self.live_id.id),
            ('main_zone_location_id','=',self.main_zone_location_id.id),
        ]):
            if str(rec.id) != str(self.id) and not self.is_sub_property:
                return {
                    'warning': {'title': _('Warning'), 'message': _('Property Data Is Repeated'), },
                }

    @api.model
    def create(self, vals):
        if vals.get('is_sub_property'):
            vals['sub_sequence'] = self.env['ir.sequence'].next_by_code('property.sub.seq')
            vals['name'] = vals['sub_sequence'] + '-' + vals['name']
        return super(Property, self).create(vals)

    def edit_status(self):
        """
        This method is used to change property state to book.
        @param self: The object pointer
        """
        return self.write({'state': 'book'})

    def edit_status_book(self):
        """
        This method will open a wizard.
        @param self: The object pointer
        """
        context = dict(self._context)
        for rec in self:
            context.update({'edit_result': rec.id})
        return {
            'name': ('wizard'),
            'res_model': 'book.available.wiz',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': context,
        }

    def open_url(self):
        """
        This Button method is used to open a URL
        according fields values.
        @param self: The object pointer
        """
        url = "http://maps.google.com/maps?oi=map&q="
        for line in self:
            if line.name:
                street_s = re.sub(r'[^\w]', ' ', line.name)
                street_s = re.sub(' +', '+', street_s)
                url += street_s + '+'
            if line.street:
                street_s = re.sub(r'[^\w]', ' ', line.street)
                street_s = re.sub(' +', '+', street_s)
                url += street_s + '+'
            if line.street2:
                street_s = re.sub(r'[^\w]', ' ', line.street2)
                street_s = re.sub(' +', '+', street_s)
                url += street_s + '+'
            if line.township:
                street_s = re.sub(r'[^\w]', ' ', line.township)
                street_s = re.sub(' +', '+', street_s)
                url += street_s + '+'
            if line.city:
                street_s = re.sub(r'[^\w]', ' ', line.city)
                street_s = re.sub(' +', '+', street_s)
                url += street_s + '+'
            if line.state_id:
                street_s = re.sub(r'[^\w]', ' ', line.state_id.name)
                street_s = re.sub(' +', '+', street_s)
                url += street_s + '+'
            if line.country_id:
                street_s = re.sub(r'[^\w]', ' ', line.country_id.name)
                street_s = re.sub(' +', '+', street_s)
                url += street_s + '+'
            if line.latitude:
                street_s = re.sub(r'[^\w]', ' ', str(line.latitude))
                street_s = re.sub(' +', '+', street_s)
                url += street_s + '+'
            if line.street2:
                street_s = re.sub(r'[^\w]', ' ', str(line.longitude))
                street_s = re.sub(' +', '+', street_s)
                url += street_s + '+'

            if line.zip:
                url += line.zip
        return {
            'name': _('Go to website'),
            'res_model': 'ir.actions.act_url',
            'type': 'ir.actions.act_url',
            'target': 'current',
            'url': url
        }

    def button_normal(self):
        """
        This Button method is used to change property state to On Lease.
        @param self: The object pointer
        """
        for rec in self:
            rec.write({'state': 'normal'})

    def button_sold(self):
        """
        This Button method is used to change property state to Sold.
        @param self: The object pointer
        """
        invoice_obj = self.env['account.invoice']
        for data in self:
            company = self.company_id
            if not company.expense_account_id:
                     raise Warning(_('Please Configure Income \
                                Account from Property!'))
            inv_line_values = {
                'name': data.name or "",
                'origin': 'account.asset',
                'quantity': 1,
                'account_id': company.income_acc_id.id or False,
                'price_unit': data.sale_price or 0.00,
            }

            inv_values = {
                'origin': data.name or "",
                'type': 'out_invoice',
                'property_id': data.id,
                'partner_id': data.customer_id.id or False,
                'payment_term_id': data.payment_term.id,
                'invoice_line_ids': [(0, 0, inv_line_values)],
                'date_invoice': datetime.now().strftime(
                    DEFAULT_SERVER_DATE_FORMAT) or False,
                # 'number': data.code or '',
            }
            invoice_obj.create(inv_values)
            data.write({'state': 'sold'})
        return True

    # def button_close(self):
    #     """
    #     This Button method is used to change property state to Sale.
    #     @param self: The object pointer
    #     """
    #     for rec in self:
    #         rec.write({'state': 'close'})

    def button_cancel(self):
        """
        This Button method is used to change property state to Cancel.
        @param self: The object pointer
        """
        for rec in self:
            rec.write({'state': 'cancel'})

    def button_draft(self):
        """
        This Button method is used to change property state to Available.
        @param self: The object pointer
        """
        for rec in self:
            rec.write({'state': 'draft'})

    def date_addition(self, starting_date, end_date, period):
        date_list = []
        if period == 'monthly':
            while starting_date < end_date:
                date_list.append(starting_date)
                res = ((
                        starting_date + relativedelta(months=1)))
                starting_date = res
            return date_list
        else:
            while starting_date < end_date:
                date_list.append(starting_date)
                res = ((
                        starting_date + relativedelta(years=1)))
                starting_date = res
            return date_list




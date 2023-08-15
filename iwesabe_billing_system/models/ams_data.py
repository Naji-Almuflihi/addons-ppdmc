# -*- coding: utf-8 -*-
##############################################################################
#
#    Global Creative Concepts Tech Co Ltd.
#    Copyright (C) 2018-TODAY iWesabe (<http://www.iwesabe.com>).
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from datetime import datetime
from odoo import api, fields, models
import pytz


class AmsData(models.Model):
    _name = 'ams.data'

    ams_id = fields.Integer('ID')
    arrival_airline = fields.Char(string="Arrival Airline")
    departure_airline = fields.Char(string="Departure Airline")
    airline = fields.Char('Airline')
    arrival_flight_no = fields.Char('Arrival Flight NO:')
    departure_flight_no = fields.Char('Departure Flight No:')
    actual_aircraft = fields.Char('Actual Aircraft')
    actual_category = fields.Char('Actual Category')
    apron = fields.Char('APRON')
    reg_no = fields.Char('Reg.NO')
    amtow = fields.Float('AMTOW')
    agha = fields.Char('AGHA')
    a_status = fields.Char('Arrival Status')
    d_status = fields.Char('Departure Status')
    a_terminal = fields.Char('Arrival Terminal')
    d_terminal = fields.Char('Departure Terminal')
    actual_a_time = fields.Datetime('Actual Arrival Time')
    actual_d_time = fields.Datetime('Actual Departure Time')
    ADT2 = fields.Char('AD2')
    a_passenger_no = fields.Integer('Actual Passenger No:')
    d_passenger_no = fields.Integer('Departure Passenger No:')
    a_stand = fields.Char('Arrival Stand')
    d_stand = fields.Char('Departure Stand')
    HN = fields.Char('HN')
    DHN = fields.Char('DHN')
    from_city = fields.Char('From City')
    to_city = fields.Char('To city')
    ABUSS = fields.Char('ABUSS')
    DBUSS = fields.Char('DBUSS')
    check_in_counter = fields.Char('Check In Counter')
    AFLT_type = fields.Char('AFLT Type')
    DFLT_type = fields.Char('DFLT Type')
    ground_time = fields.Char(string="Ground Time", required=False, )
    origin_type = fields.Char('Origin Type')
    destination_type = fields.Char('Destination Type')
    partner_id = fields.Many2one('res.partner', string='Customer')

    condition1 = fields.Boolean(string="Apron Null", compute='check_data', store=True)
    condition2 = fields.Boolean(string="Total Number Of Flights With MTOW = Null In APRON6", compute='check_data', store=True)
    condition3 = fields.Boolean(string="Total Number Of Flights With Arrival Stand 6-1,6-2,6-3,6-4,6-5,6-6,6-7,6-8,6-9,6-10 with Buses", compute='check_data', store=True)
    condition4 = fields.Boolean(string="Total Number Of Flights With Departure Stand 6-1,6-2,6-3,6-4,6-5,6-6,6-7,6-8,6-9,6-10 with Buses", compute='check_data', store=True)
    condition5 = fields.Boolean(string="Total Number Of Flights With Invalid ground time in Apron6", compute='check_data', store=True)  # FIXME less data
    condition6 = fields.Boolean(string="Total Number Of International Airlines With Domestic Origin", compute='check_data', store=True)  # FIXME less data
    condition11 = fields.Boolean(string="Total Number Of International Airlines With Domestic Destination", compute='check_data', store=True)  # FIXME less data

    condition7 = fields.Boolean(string="Total Number With Invalid Arrival Terminal", compute='check_data', store=True)
    condition8 = fields.Boolean(string="Total Number With Invalid Departure Terminal", compute='check_data', store=True)
    condition9 = fields.Boolean(string="Total Number With Invalid Arrival I/D Flag", compute='check_data', store=True)
    condition10 = fields.Boolean(string="Total Number With Invalid Departure I/D Flag", compute='check_data', store=True)
    actual_a_time_date = fields.Date(string="", required=False, compute='get_a_time_and_d_time_dates', store=True)
    actual_d_time_date = fields.Date(string="", required=False, compute='get_a_time_and_d_time_dates', store=True)

    @api.model
    def create(self, vals):
        res = super(AmsData, self).create(vals)
        air = res['arrival_airline']
        partner_id = self.env['res.partner'].search([('airline_code', '=', air), ('is_airline', '=', True)])
        res['partner_id'] = partner_id.id
        return res       

    def _get_check_time(self, check_date):
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        tz = pytz.timezone((self.env.user.tz or 'UTC'))
        checkdate = pytz.utc.localize(datetime.strptime(str(check_date), DATETIME_FORMAT)).astimezone(tz)
        return checkdate

    @api.depends('actual_a_time', 'actual_d_time')
    def get_a_time_and_d_time_dates(self):
        for rec in self:
            if rec.actual_a_time:
                actual_a_time = self._get_check_time(rec.actual_a_time)
                rec.actual_a_time_date = actual_a_time.date()
            else:
                rec.actual_a_time_date = False
            if rec.actual_d_time:
                actual_d_time = self._get_check_time(rec.actual_d_time)
                rec.actual_d_time_date = actual_d_time.date()
            else:
                rec.actual_a_time_date = False

    @api.depends('apron', 'amtow', 'a_status', 'DBUSS', 'ABUSS', 'd_stand', 'a_terminal', 'd_terminal', 'AFLT_type', 'DFLT_type', 'ground_time', 'origin_type', 'destination_type')
    def check_data(self):
        for rec in self:
            if not rec.apron:
                rec.condition1 = True
            else:
                rec.condition1 = False
            if rec.amtow and rec.apron == 'Apron6':
                rec.condition2 = True
            else:
                rec.condition2 = False
            if rec.a_stand in ['6-1', '6-2', '6-3', '6-4', '6-5', '6-6', '6-7', '6-8', '6-9', '6-10'] and rec.ABUSS == 'BUSES':
                rec.condition3 = True
            else:
                rec.condition3 = False
            if rec.d_stand in ['6-1', '6-2', '6-3', '6-4', '6-5', '6-6', '6-7', '6-8', '6-9', '6-10'] and rec.DBUSS == 'BUSES':
                rec.condition4 = True
            else:
                rec.condition4 = False
            if rec.apron == 'Apron6' and int(rec.ground_time) < 0:
                rec.condition5 = True
            else:
                rec.condition5 = False
            if (rec.AFLT_type == 'I' or rec.DFLT_type == 'I') and rec.origin_type == 'D':
                rec.condition6 = True
            else:
                rec.condition6 = False
            if (rec.AFLT_type == 'I' or rec.DFLT_type == 'I') and rec.destination_type == 'D':
                rec.condition11 = True
            else:
                rec.condition11 = False
            if rec.a_terminal not in ['N', 'H', 'S', 'T1']:
                rec.condition7 = True
            else:
                rec.condition7 = False
            if rec.d_terminal not in ['N', 'H', 'S', 'T1']:
                rec.condition8 = True
            else:
                rec.condition8 = False
            if rec.AFLT_type not in ['I', 'D']:
                rec.condition9 = True
            else:
                rec.condition9 = False
            if rec.DFLT_type not in ['I', 'D']:
                rec.condition10 = True
            else:
                rec.condition10 = False




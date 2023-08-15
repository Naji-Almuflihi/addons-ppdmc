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
import pytz
from datetime import timedelta
import calendar
from datetime import date
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime

from_string = fields.Date.from_string
to_string = fields.Date.to_string


MONTH_LIMIT = 10

EXIST_ACTION_TYPES = [
    ('alert', 'Show Message.'),
    ('ignore', 'Ignore New Data.'),
    ('replace', 'Overwrite Existing Data.'),
]


class AmsInstanceLoad(models.TransientModel):
    _name = 'ams.instance.load'

    @staticmethod
    def default_dates():
        today = date.today()
        n = calendar.monthrange(today.year, today.month)[1]
        return {'from': to_string(today.replace(day=1)), 'to': to_string(today.replace(day=n)), }

    instance_id = fields.Many2one('ams.billing.instance', string='Instance')
    summary = fields.Html(default=False, readonly=True)
    date_from = fields.Date(required=True, string='From', default=fields.Date.context_today)
    date_to = fields.Date(required=True, string='To', default=fields.Date.context_today)
    show_reimport = fields.Boolean(string="",compute='check_validation'  )
    show_load = fields.Boolean(string="",compute='check_load_button'  )

    @api.depends('date_from','date_to')
    def check_load_button(self):
        ams_data = self.env['ams.data'].search([('actual_a_time_date','>=',self.date_from),('actual_a_time_date','<=',self.date_to)])
        if ams_data:
            self.show_load = False
        else:
            self.show_load = True


    def check_ams_conn(self, raise_if_succeded=True):
        if not self.instance_id:
            return
        self.instance_id.check_connection(raise_if_succeded=raise_if_succeded)

    def check_data_already(self, ams_id):

        if not ams_id:
            return
        data_id = self.env['ams.data'].search([('ams_id', '=', ams_id)])
        if data_id:
            return data_id
        return False

    def insert_ams_data(self, instance_id, data):
        data_id = self.env['ams.data'].create(data)
        if data_id:
            res = 'inserted'
            return res

    def update_ams_data(self, instance_id, data):

        data_id = self.check_data_already(data['ams_id'])

        if data_id:
            return 'ignored_already'
        else:
            insert_update = self.insert_ams_data(data=data, instance_id=instance_id)
            return insert_update

    def update_instance_ams_data(self, instance_id, date_from, date_to):
        status = {'inserted': 0,'ignored_already': 0, 'record_count': 0}

        for each in instance_id.get_all_data(date_from,date_to):
            status['record_count'] += 1
            res = self.sudo().update_ams_data(instance_id, each)
            if res == 'inserted':
                status['inserted'] += 1
            if res == 'ignored_already':
                status['ignored_already'] += 1

        return status

    def validate_ams_data(self):
        self.ensure_one()

        try:

            self.check_ams_conn(raise_if_succeded=False)

            if not self.instance_id or not self.date_from or not self.date_to:
                raise UserError('Fields are not correctly set!')

            status = self.update_instance_ams_data(
                instance_id=self.instance_id,
                date_from=self.date_from,
                date_to=self.date_to,
            )

            html_status = ''
            chevron = '<i class="fa fa-chevron-right"/>'

            html_status = html_status + '<br/>%s\tTotal:\t%s Records.' % (chevron, status['record_count'])

            if status['inserted']:
                html_status = html_status + '<br/>%s\tInserted:\t%s Records.' % (chevron, status['inserted'])

            if status['ignored_already']:
                html_status = html_status + '<br/>%s\t%s Records are already loaded(Ignored).' % (chevron, status['ignored_already'])

            self.summary = html_status

        except Exception as e:
            raise UserError(e.args[0])

    @api.depends('date_from', 'date_to')
    def check_validation(self):
        ams_data = self.env['ams.data'].search(
            [('actual_a_time_date', '>=', self.date_from), ('actual_d_time_date', '<=', self.date_to)])

        # for rec in ams_data:
        #     if rec.actual_a_time

        condition1 = ams_data.search_count([('condition1', '=', True)])
        condition2 = ams_data.search_count([('condition2', '=', True)])
        condition3 = ams_data.search_count([('condition3', '=', True)])
        condition4 = ams_data.search_count([('condition4', '=', True)])
        condition5 = ams_data.search_count([('condition5', '=', True)])
        condition6 = ams_data.search_count([('condition6', '=', True)])
        condition11 = ams_data.search_count([('condition11', '=', True)])
        condition7 = ams_data.search_count([('condition7', '=', True)])
        condition8 = ams_data.search_count([('condition8', '=', True)])
        condition9 = ams_data.search_count([('condition9', '=', True)])
        condition10 = ams_data.search_count([('condition10', '=', True)])

        if condition1 or condition2 or condition3 or condition4 or condition5 or condition6 or condition7 or condition8 or condition9 or condition10 or condition11:
            self.show_reimport = True
        else:
            self.show_reimport = False

    def run_validation(self):
        return {
            'name': 'Validations',
            'view_mode': 'form',
            'res_model': 'ams.data.validation',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {'default_from_date':self.date_from,'default_to_date':self.date_to },
        }

    def reimport_data(self):
        pass






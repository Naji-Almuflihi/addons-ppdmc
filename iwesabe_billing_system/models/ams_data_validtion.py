from odoo import models, fields, api
from datetime import datetime


class AmsDataValidation(models.Model):
    _name = 'ams.data.validation'

    from_date = fields.Date(string="From Date", required=True, )
    to_date = fields.Date(string="To Date", required=True, )

    condition1 = fields.Integer(string="Apron Null",readonly=True,compute='get_count')
    condition2 = fields.Integer(string="Total Number Of Flights With MTOW = Null In APRON6",readonly=True,compute='get_count')
    condition3 = fields.Integer(
        string="Total Number Of Flights With Arrival Stand 6-1,6-2,6-3,6-4,6-5,6-6,6-7,6-8,6-9,6-10 with Buses",readonly=True,compute='get_count',)
    condition4 = fields.Integer(
        string="Total Number Of Flights With Departure Stand 6-1,6-2,6-3,6-4,6-5,6-6,6-7,6-8,6-9,6-10 with Buses",readonly=True,compute='get_count',)
    condition5 = fields.Integer(string="Total Number Of Flights With Invalid ground time in Apron6",readonly=True,compute='get_count',)  # FIXME less data
    condition6 = fields.Integer(string="Total Number Of International Airlines With Domestic Origin",readonly=True,compute='get_count',)  # FIXME less data
    condition11 = fields.Integer(string="Total Number Of International Airlines With Domestic Destination",readonly=True,compute='get_count',)  # FIXME less data

    condition7 = fields.Integer(string="Total Number With Invalid Arrival Terminal",readonly=True,compute='get_count',)
    condition8 = fields.Integer(string="Total Number With Invalid Departure Terminal",readonly=True,compute='get_count',)
    condition9 = fields.Integer(string="Total Number With Invalid Arrival I/D Flag",readonly=True,compute='get_count',)
    condition10 = fields.Integer(string="Total Number With Invalid Departure I/D Flag",readonly=True,compute='get_count',)

    @api.depends('from_date','to_date')
    def get_count(self):
        self.condition1 = 0
        self.condition2 = 0
        self.condition3 = 0
        self.condition4 = 0
        self.condition5 = 0
        self.condition6 = 0
        self.condition7 = 0
        self.condition8 = 0
        self.condition9 = 0
        self.condition10 = 0
        self.condition11 = 0
        if self.from_date and self.to_date:
            # dateformat = '%Y-%m-%d %H:%M:%S'
            # date_from = datetime.strptime(str(self.date_from), dateformat).date()
            # date_to = datetime.strptime(str(self.date_to), dateformat).date()
            ams_data = self.env['ams.data'].search([])
            print('kkkkkkkkkkkkkkkkkkkkkkk')

            # dateformat = '%Y-%m-%d'
            # date_from = datetime.strptime(str(self.date_from), dateformat).date()
            # date_to = datetime.strptime(str(self.date_to), dateformat).date()
            #
            # for rec in ams_data:
            #     actual_a_time = datetime.strptime(str(rec.actual_a_time), dateformat).date()
            #     actual_d_time = datetime.strptime(str(rec.actual_d_time), dateformat).date()
            #     if rec.actual_a_time >= self.from_date and rec.actual_d_time <= self.to_date:
            #         if rec.condition
            #         condition1 += 1

            self.condition1 = ams_data.search_count([('condition1','=',True),('actual_a_time_date','>=',self.from_date),('actual_d_time_date','<=',self.to_date)])
            self.condition2 = ams_data.search_count([('condition2','=',True),('actual_a_time_date','>=',self.from_date),('actual_d_time_date','<=',self.to_date)])
            self.condition3 = ams_data.search_count([('condition3','=',True),('actual_a_time_date','>=',self.from_date),('actual_d_time_date','<=',self.to_date)])
            self.condition4 = ams_data.search_count([('condition4','=',True),('actual_a_time_date','>=',self.from_date),('actual_d_time_date','<=',self.to_date)])
            self.condition5 = ams_data.search_count([('condition5','=',True),('actual_a_time_date','>=',self.from_date),('actual_d_time_date','<=',self.to_date)])
            self.condition6 = ams_data.search_count([('condition6','=',True),('actual_a_time_date','>=',self.from_date),('actual_d_time_date','<=',self.to_date)])
            self.condition11 = ams_data.search_count([('condition11','=',True),('actual_a_time_date','>=',self.from_date),('actual_d_time_date','<=',self.to_date)])
            self.condition7 = ams_data.search_count([('condition7','=',True),('actual_a_time_date','>=',self.from_date),('actual_d_time_date','<=',self.to_date)])
            self.condition8 = ams_data.search_count([('condition8','=',True),('actual_a_time_date','>=',self.from_date),('actual_d_time_date','<=',self.to_date)])
            self.condition9 = ams_data.search_count([('condition9','=',True),('actual_a_time_date','>=',self.from_date),('actual_d_time_date','<=',self.to_date)])
            self.condition10 = ams_data.search_count([('condition10','=',True),('actual_a_time_date','>=',self.from_date),('actual_d_time_date','<=',self.to_date)])

    def open_condition1(self):
        return {
            'name': 'Apron Null',
            'view_mode': 'tree,form',
            'res_model': 'ams.data',
            'domain': [('condition1', '=', True),('actual_a_time_date','>=',self.from_date),('actual_d_time_date','<=',self.to_date)],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {'create': False, 'edit': False, },
        }

    def open_condition2(self):
        return {
            'name': 'Total Number Of Flights With MTOW = Null In APRON6',
            'view_mode': 'tree,form',
            'res_model': 'ams.data',
            'domain': [('condition2', '=', True),('actual_a_time_date','>=',self.from_date),('actual_d_time_date','<=',self.to_date)],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {'create': False, 'edit': False, },
        }

    def open_condition3(self):
        return {
            'name': 'Total Number Of Flights With Arrival Stand 6-1,6-2,6-3,6-4,6-5,6-6,6-7,6-8,6-9,6-10 with Buses',
            'view_mode': 'tree,form',
            'res_model': 'ams.data',
            'domain': [('condition3', '=', True),('actual_a_time_date','>=',self.from_date),('actual_d_time_date','<=',self.to_date)],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {'create': False, 'edit': False, },
        }

    def open_condition4(self):
            return {
                'name': 'Total Number Of Flights With Departure Stand 6-1,6-2,6-3,6-4,6-5,6-6,6-7,6-8,6-9,6-10 with Buses',
                'view_mode': 'tree,form',
                'res_model': 'ams.data',
                'domain': [('condition4', '=', True),('actual_a_time_date','>=',self.from_date),('actual_d_time_date','<=',self.to_date)],
                'type': 'ir.actions.act_window',
                'target': 'current',
                'context': {'create': False, 'edit': False, },
            }

    def open_condition5(self):
            return {
                'name': 'Total Number Of Flights With Invalid ground time in Apron6',
                'view_mode': 'tree,form',
                'res_model': 'ams.data',
                'domain': [('condition5', '=', True),('actual_a_time_date','>=',self.from_date),('actual_d_time_date','<=',self.to_date)],
                'type': 'ir.actions.act_window',
                'target': 'current',
                'context': {'create': False, 'edit': False, },
            }

    def open_condition6(self):
                return {
                    'name': 'Total Number Of International Airlines With Domestic Origin',
                    'view_mode': 'tree,form',
                    'res_model': 'ams.data',
                    'domain': [('condition6', '=', True),('actual_a_time_date','>=',self.from_date),('actual_d_time_date','<=',self.to_date)],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'context': {'create': False, 'edit': False, },
                }

    def open_condition7(self):
        return {
            'name': 'Total Number With Invalid Arrival Terminal',
            'view_mode': 'tree,form',
            'res_model': 'ams.data',
            'domain': [('condition7', '=', True),('actual_a_time_date','>=',self.from_date),('actual_d_time_date','<=',self.to_date)],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {'create': False, 'edit': False, },
        }

    def open_condition8(self):
        return {
            'name': 'Total Number With Invalid Departure Terminal',
            'view_mode': 'tree,form',
            'res_model': 'ams.data',
            'domain': [('condition8', '=', True), ('actual_a_time_date', '>=', self.from_date), ('actual_d_time_date', '<=', self.to_date)],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {'create': False, 'edit': False, },
        }

    def open_condition9(self):
        return {
            'name': 'Total Number With Invalid Arrival I/D Flag',
            'view_mode': 'tree,form',
            'res_model': 'ams.data',
            'domain': [('condition9', '=', True), ('actual_a_time_date', '>=', self.from_date), ('actual_d_time_date', '<=', self.to_date)],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {'create': False, 'edit': False, },
        }

    def open_condition10(self):
        return {
            'name': 'Total Number With Invalid Departure I/D Flag',
            'view_mode': 'tree,form',
            'res_model': 'ams.data',
            'domain': [('condition10', '=', True), ('actual_a_time_date', '>=', self.from_date), ('actual_d_time_date', '<=', self.to_date)],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {'create': False, 'edit': False, },
        }

    def open_condition11(self):
        return {
            'name': 'Total Number Of International Airlines With Domestic Destination',
            'view_mode': 'tree,form',
            'res_model': 'ams.data',
            'domain': [('condition11', '=', True), ('actual_a_time_date', '>=', self.from_date), ('actual_d_time_date', '<=', self.to_date)],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {'create': False, 'edit': False, },
        }

from odoo import models, fields
from datetime import datetime


class GenerateRevenue(models.TransientModel):
    _name = 'generate.revenue'
    _description = ''

    from_date = fields.Date(string="From Date", required=False, default=fields.Date.context_today)
    to_date = fields.Date(string="To Date", required=False, default=fields.Date.context_today)
    partner_id = fields.Many2one("res.partner", string="Partner", domain=[('is_airline', '=', True)])

    def generate_revenue(self):
        ams_data = self.env['ams.data'].search([('airline', '=', self.partner_id.airline_code), ('actual_a_time_date', '>=', self.from_date), ('actual_d_time_date', '<=', self.to_date)])
        airline_data = []
        for dt in ams_data:
            actual_a_time = datetime.strptime(str(dt.actual_a_time), "%Y-%m-%d %H:%M:%S")
            actual_d_time = datetime.strptime(str(dt.actual_d_time), "%Y-%m-%d %H:%M:%S")
            ground_time = (actual_d_time - actual_a_time)
            minute = ground_time.seconds / 60
            hour = minute / 60
            if dt.arrival_flight_no and dt.departure_flight_no:
                airline_data.append((0, 0, {
                    'ams_id': dt.ams_id,
                    'actual_a_time': dt.actual_a_time,
                    'actual_d_time': dt.actual_d_time,
                    'mode': 'a',
                    'apron': dt.apron,
                    'parking_stand': dt.a_stand,
                    'aircraft_registration': dt.reg_no,
                    'actual_aircraft': dt.actual_aircraft,
                    'actual_category': dt.actual_category,
                    'amtow': dt.amtow,
                    'airline': dt.airline,
                    'agha': dt.agha,
                    'flight_no': dt.arrival_flight_no,
                    'flight_type': dt.a_status,
                    'pax': dt.a_passenger_no,
                    'terminal': dt.a_terminal,
                    'counter': dt.check_in_counter,
                    'ground_time': hour,
                    'FLT_type': dt.AFLT_type,
                }))

                airline_data.append((0, 0, {
                    'ams_id': dt.ams_id,
                    'actual_a_time': dt.actual_a_time,
                    'actual_d_time': dt.actual_d_time,
                    'mode': 'd',
                    'apron': dt.apron,
                    'parking_stand': dt.d_stand,
                    'aircraft_registration': dt.reg_no,
                    'actual_aircraft': dt.actual_aircraft,
                    'actual_category': dt.actual_category,
                    'amtow': dt.amtow,
                    'airline': dt.airline,
                    'agha': dt.agha,
                    'flight_no': dt.departure_flight_no,
                    'flight_type': dt.d_status,
                    'pax': dt.d_passenger_no,
                    'terminal': dt.d_terminal,
                    'counter': dt.check_in_counter,
                    'ground_time': hour,
                    'FLT_type': dt.DFLT_type,
                }))
            elif dt.arrival_flight_no and not dt.departure_flight_no:
                airline_data.append((0, 0, {
                    'ams_id': dt.ams_id,
                    'actual_a_time': dt.actual_a_time,
                    'actual_d_time': dt.actual_d_time,
                    'mode': 'a',
                    'apron': dt.apron,
                    'parking_stand': dt.a_stand,
                    'aircraft_registration': dt.reg_no,
                    'actual_aircraft': dt.actual_aircraft,
                    'actual_category': dt.actual_category,
                    'amtow': dt.amtow,
                    'airline': dt.airline,
                    'agha': dt.agha,
                    'flight_no': dt.arrival_flight_no,
                    'flight_type': dt.a_status,
                    'pax': dt.a_passenger_no,
                    'terminal': dt.a_terminal,
                    'counter': dt.check_in_counter,
                    'ground_time': hour,
                    'FLT_type': dt.AFLT_type,
                }))
            elif not dt.arrival_flight_no and dt.departure_flight_no:
                airline_data.append((0, 0, {
                    'ams_id': dt.ams_id,
                    'actual_a_time': dt.actual_a_time,
                    'actual_d_time': dt.actual_d_time,
                    'mode': 'd',
                    'apron': dt.apron,
                    'parking_stand': dt.d_stand,
                    'aircraft_registration': dt.reg_no,
                    'actual_aircraft': dt.actual_aircraft,
                    'actual_category': dt.actual_category,
                    'amtow': dt.amtow,
                    'airline': dt.airline,
                    'agha': dt.agha,
                    'flight_no': dt.departure_flight_no,
                    'flight_type': dt.d_status,
                    'pax': dt.d_passenger_no,
                    'terminal': dt.d_terminal,
                    'counter': dt.check_in_counter,
                    'ground_time': hour,
                    'FLT_type': dt.DFLT_type,
                }))

        invoice_appendix = self.env['invoice.appendix'].create({
            'from_date': self.from_date,
            'to_date': self.to_date,
            'partner_id': self.partner_id.id,
            'invoice_appendix_line_ids': airline_data,
        })

        open_view_id = self.env.ref(
            'iwesabe_billing_system.view_invoice_appendix_form').id
        return {
            'view_type': 'form',
            'view_id': open_view_id,
            'view_mode': 'form',
            'res_model': 'invoice.appendix',
            'res_id': invoice_appendix and invoice_appendix.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': self._context,
        }

 # -*- coding: utf-8 -*-
from odoo.http import request
from odoo import models, api,fields
from odoo import SUPERUSER_ID
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import pytz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from dateutil import parser


class invoice_appendix_reportXls(models.AbstractModel):
    _name = 'report.iwesabe_billing_system.invoice_appendix_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def _get_actual_date_time(self, check_date):
        user_id = self.env['res.users']
        user = user_id.browse(SUPERUSER_ID)
        tz = pytz.timezone((self.env.user.tz or 'UTC'))
        checkdate = pytz.utc.localize(datetime.strptime(str(check_date), DATETIME_FORMAT)).astimezone(tz).replace(tzinfo=None)
        return checkdate

    def generate_xlsx_report(self, workbook, data, inv_app):
        worksheet = workbook.add_worksheet("Invoice Appendix Report")
        # worksheet.right_to_left()
        f1 = workbook.add_format({'bold': True, 'font_color': '#000000', 'border': False, 'align': 'center', 'num_format': '#,##0.00'})
        f2 = workbook.add_format({'bold': True, 'font_color': '#000000', 'size': 10, 'border': False, 'align': 'center','num_format': '#,##0.00','fg_color': 'DCDCDC',})
        cell_text_format = workbook.add_format({'align': 'center',
                                                'bold': True,
                                                'border': 1,
                                                'size': 10,
                                                'fg_color': '#a8d5e5',
                                                'num_format': '#,##0.00',
                                                })
        cell_text_format_values = workbook.add_format({'align': 'center',
                                                       'bold': False,
                                                       'border': 1,
                                                       'size': 9,
                                                       'fg_color': 'E0FFFF',
                                                       'num_format': '#,##0.00'
                                                               })
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 16)
        worksheet.set_column('C:C', 16)
        worksheet.set_column('D:D', 18)
        worksheet.set_column('E:E', 7)
        worksheet.set_column('F:F', 10)
        worksheet.set_column('G:G', 12)
        worksheet.set_column('H:H', 16)
        worksheet.set_column('I:I', 12)
        worksheet.set_column('J:J', 14)
        worksheet.set_column('K:K', 10)
        worksheet.set_column('L:L', 10)
        worksheet.set_column('M:M', 12)
        worksheet.set_column('N:N', 8)
        worksheet.set_column('O:O', 12)
        worksheet.set_column('P:P', 8)
        worksheet.set_column('Q:Q', 8)
        worksheet.set_column('R:R', 10)
        worksheet.set_column('S:S', 18)
        # worksheet.set_column('T:T', 24)
        # worksheet.set_column('U:U', 8)
        # worksheet.set_column('V:V', 10)
        # worksheet.set_column('W:W', 18)
        # worksheet.set_column('X:X', 26)
        # worksheet.set_column('Y:Y', 16)
        # worksheet.set_column('Z:Z', 10)
        # worksheet.set_column('AA:AA', 13)

        row = 0
        col = -1
        worksheet.merge_range(row + 2, col + 1, row + 2, col + 8,
                        'Actual Traffic From ' + str(inv_app.from_date) + ' to ' + str(inv_app.to_date) + ' For ' + str(inv_app.partner_id.name) + ' ( ' + str(len(inv_app.invoice_appendix_line_ids)) + ' ) Movements', f1)

        worksheet.write(row + 5, col + 1, 'ID', cell_text_format)
        worksheet.write(row + 5, col + 2, 'Last update', cell_text_format)
        worksheet.write(row + 5, col + 3, 'Flight Arrival date', cell_text_format)
        worksheet.write(row + 5, col + 4, 'Flight Departure date', cell_text_format)
        worksheet.write(row + 5, col + 5, 'Mode', cell_text_format)
        worksheet.write(row + 5, col + 6, 'APRON', cell_text_format)
        worksheet.write(row + 5, col + 7, 'Parking Stand', cell_text_format)
        worksheet.write(row + 5, col + 8, 'Actual Registration', cell_text_format)
        worksheet.write(row + 5, col + 9, 'Aircraft Type', cell_text_format)
        worksheet.write(row + 5, col + 10, 'Aircraft Category', cell_text_format)
        worksheet.write(row + 5, col + 11, 'AMTOW', cell_text_format)
        worksheet.write(row + 5, col + 12, 'Airline Code', cell_text_format)
        worksheet.write(row + 5, col + 13, 'Handling Agent', cell_text_format)
        worksheet.write(row + 5, col + 14, 'Flight NO', cell_text_format)
        worksheet.write(row + 5, col + 15, 'Flight Type', cell_text_format)
        worksheet.write(row + 5, col + 16, 'PAX', cell_text_format)
        worksheet.write(row + 5, col + 17, 'Terminal', cell_text_format)
        worksheet.write(row + 5, col + 18, 'Counter', cell_text_format)
        worksheet.write(row + 5, col + 19, 'Ground Time', cell_text_format)
        col_count = 20
        for billing_pricing in inv_app.billing_pricing_ids.filtered(lambda b: b.appendix_total_field):
            len_pricing = (len(billing_pricing.name) + 4) if len(billing_pricing.name) < 6 else len(
                billing_pricing.name)
            worksheet.set_column(col + col_count, col + col_count, len_pricing)
            worksheet.write(row + 5, col + col_count, billing_pricing.name, cell_text_format)
            col_count += 1
        worksheet.set_column(col + col_count, col + col_count, 16)
        worksheet.write(row + 5, col + col_count, 'Total', cell_text_format)
        row = 6
        seq = 0

        for inv_appendix in inv_app.invoice_appendix_line_ids:
            row += 1
            seq += 1
            worksheet.write(row, col + 1, str(inv_appendix.ams_id), cell_text_format_values)
            worksheet.write(row, col + 2, str(self._get_actual_date_time(parser.parse(str(inv_appendix.last_updated_date)).strftime("%Y-%m-%d %H:%M:%S")) or ''), cell_text_format_values)
            worksheet.write(row, col + 3, str(self._get_actual_date_time(inv_appendix.actual_a_time) or ''), cell_text_format_values)
            worksheet.write(row, col + 4, str(self._get_actual_date_time(inv_appendix.actual_d_time) or ' '), cell_text_format_values)
            worksheet.write(row, col + 5, str(inv_appendix.mode), cell_text_format_values)
            worksheet.write(row, col + 6, str(inv_appendix.apron), cell_text_format_values)
            worksheet.write(row, col + 7, str(inv_appendix.parking_stand), cell_text_format_values)
            worksheet.write(row, col + 8, str(inv_appendix.aircraft_registration), cell_text_format_values)
            worksheet.write(row, col + 9, str(inv_appendix.actual_aircraft), cell_text_format_values)
            worksheet.write(row, col + 10, str(inv_appendix.actual_category), cell_text_format_values)
            worksheet.write(row, col + 11, inv_appendix.amtow, cell_text_format_values)
            worksheet.write(row, col + 12, str(inv_appendix.airline), cell_text_format_values)
            worksheet.write(row, col + 13, str(inv_appendix.agha), cell_text_format_values)
            worksheet.write(row, col + 14, str(inv_appendix.flight_no), cell_text_format_values)
            worksheet.write(row, col + 15, str(inv_appendix.flight_type), cell_text_format_values)
            worksheet.write(row, col + 16, str(inv_appendix.pax), cell_text_format_values)
            worksheet.write(row, col + 17, str(inv_appendix.terminal), cell_text_format_values)
            worksheet.write(row, col + 18, str(inv_appendix.counter), cell_text_format_values)
            worksheet.write(row, col + 19, str(timedelta(hours=inv_appendix.ground_time)).rsplit(':', 1)[0], cell_text_format_values)
            col_count = 20
            for billing_pricing in inv_app.billing_pricing_ids.filtered(lambda b: b.appendix_line_value_field):
                worksheet.write(row, col + col_count, inv_appendix[billing_pricing.appendix_line_value_field.name],
                                cell_text_format_values)
                col_count += 1
            worksheet.write(row, col + col_count, inv_appendix.fees_total, cell_text_format_values)

        row += 1
        worksheet.write(row, col + 1, str('Total'), f2)
        col_count = 20
        for billing_pricing in inv_app.billing_pricing_ids.filtered(lambda b: b.appendix_total_field):
            worksheet.write(row, col + col_count, round(inv_app[billing_pricing.appendix_total_field.name], 2), f2)
            col_count += 1
        worksheet.write(row, col + col_count, round(inv_app.fees_total_total, 2), f2)

        # row = 4
        # # worksheet.write(row, col + 1, str('Total'), cell_text_format_values)
        # worksheet.write(row, col + 19, round(inv_app.term_facilities_utilization_total, 2), f2)
        # worksheet.write(row, col + 20, str(round(inv_app.systems_total, 2)), f2)
        # worksheet.write(row, col + 21, str(round(inv_app.field_400_hz_total, 2)), f2)
        # worksheet.write(row, col + 22, str(round(inv_app.ground_handling_total, 2)), f2)
        # worksheet.write(row, col + 23, str(round(inv_app.aircraft_parking_not_registered_total, 2)), f2)
        # worksheet.write(row, col + 24, str(round(inv_app.aircraft_registered_total, 2)), f2)
        # worksheet.write(row, col + 25, str(round(inv_app.plb_busses_total, 2)), f2)
        # worksheet.write(row, col + 26, str(round(inv_app.security_services_total, 2)), f2)
        # worksheet.write(row, col + 27, str(round(inv_app.fees_total_total, 2)), f2)



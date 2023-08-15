 # -*- coding: utf-8 -*-

from datetime import datetime, timedelta, date
import time
from pytz import timezone
from odoo import api, fields, models, _
from odoo import SUPERUSER_ID
import pytz
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from datetime import datetime, date, time
import pytz
from datetime import datetime, timedelta



class flight_movement_reportXls(models.AbstractModel):
    _name = 'report.iwesabe_billing_system.flight_movement_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def _get_check_time(self, check_date):
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        user_id = self.env['res.users']
        user = user_id.browse(SUPERUSER_ID)
        tz = pytz.timezone((self.env.user.tz or 'UTC'))
        checkdate = pytz.utc.localize(datetime.strptime(str(check_date), DATETIME_FORMAT)).astimezone(tz)
        return checkdate

    def generate_xlsx_report(self, workbook, data, lines):
        name =  data['form']
        worksheet = workbook.add_worksheet("Flight Movement Report")
        # worksheet.right_to_left()
        f1 = workbook.add_format(
            {'bold': True, 'font_color': '#000000', 'border': False, 'align': 'center', 'num_format': '#,##0.00'})
        f2 = workbook.add_format({'bold': True, 'font_color': '#000000', 'size': 7, 'border': 1, 'align': 'center',
                                  'num_format': '#,##0.00', 'fg_color': 'DCDCDC', })
        cell_text_format = workbook.add_format({'align': 'center',
                                                'bold': True,
                                                'border': 1,
                                                'size': 7,
                                                'fg_color': '#a8d5e5',
                                                'num_format': '#,##0.00',
                                                })
        cell_text_format_values = workbook.add_format({'align': 'center',
                                                       'bold': False,
                                                       'border': 1,
                                                       'size': 6,
                                                       'fg_color': 'E0FFFF',
                                                       'num_format': '#,##0.00'
                                                       })
        worksheet.set_column('A:A', 8)
        worksheet.set_column('B:B', 5)
        worksheet.set_column('C:C', 5)
        worksheet.set_column('D:D', 5)
        worksheet.set_column('E:E', 5)
        worksheet.set_column('F:F', 5)
        worksheet.set_column('G:G', 5)
        worksheet.set_column('H:H', 5)
        worksheet.set_column('I:I', 5)
        worksheet.set_column('J:J', 2)
        worksheet.set_column('K:K', 5)
        worksheet.set_column('L:L', 5)
        worksheet.set_column('M:M', 5)
        worksheet.set_column('N:N', 5)
        worksheet.set_column('O:O', 5)
        worksheet.set_column('P:P', 5)
        worksheet.set_column('Q:Q', 5)
        worksheet.set_column('R:R', 5)
        worksheet.set_column('S:S', 5)
        worksheet.set_column('T:T', 5)
        worksheet.set_column('U:U', 5)
        worksheet.set_column('V:V', 5)
        worksheet.set_column('W:W', 5)
        worksheet.set_column('X:X', 5)
        worksheet.set_column('Y:Y', 5)
        worksheet.set_column('Z:Z', 5)
        from_date = self._get_check_time(lines.from_date)
        to_date = self._get_check_time(lines.to_date)

        row = 0
        col = -1
        worksheet.merge_range('B2:R2','King Abdulaziz International Airport ', f1)
        worksheet.merge_range('B2:R2','Haj and Umrah Daily Passengers and Flight Movement Report ', f1)
        worksheet.merge_range('B3:R3',str(from_date.date()) + ' To ' + str(to_date.date()), f1)
        worksheet.merge_range('B4:R4','مطـار الملك عبد العزيز الدولـي', f1)
        worksheet.merge_range('B5:R5','تقرير يومي بعدد الركاب والرحلات للحجاج والمعتمرين', f1)

        worksheet.merge_range("B7:I7", 'Arrival By Terminals \n الوصول بحسب الصـالة', cell_text_format)
        worksheet.merge_range("K7:R7", 'Departure By Terminals \n المغـادرة بحسب الصـالة', cell_text_format)
        worksheet.merge_range("B8:C8", 'Haj \n الحج', cell_text_format)
        worksheet.merge_range("D8:E8", 'North \n الشمالية', cell_text_format)
        worksheet.merge_range("F8:G8", 'South \n الجنوبية', cell_text_format)
        worksheet.merge_range("H8:I8", 'Total \n المجموع', cell_text_format)
        worksheet.write("J8:J8", '',)
        worksheet.merge_range("K8:L8", 'Haj \n الحج', cell_text_format)
        worksheet.merge_range("M8:N8", 'North \n الشمالية', cell_text_format)
        worksheet.merge_range("O8:P8", 'South \n الجنوبية', cell_text_format)
        worksheet.merge_range("Q8:R8", 'Total \n المجموع', cell_text_format)
        worksheet.merge_range("A9:A10", 'Date', cell_text_format)
        worksheet.merge_range("B9:B10", 'FLTS \n رحلات', cell_text_format)
        worksheet.merge_range("C9:C10", 'PAX \n ركاب', cell_text_format)
        worksheet.merge_range("D9:D10", 'FLTS \n رحلات', cell_text_format)
        worksheet.merge_range("E9:E10", 'PAX \n ركاب', cell_text_format)
        worksheet.merge_range("F9:F10", 'FLTS \n رحلات', cell_text_format)
        worksheet.merge_range("G9:G10", 'PAX \n ركاب', cell_text_format)
        worksheet.merge_range("H9:H10", 'FLTS \n رحلات', cell_text_format)
        worksheet.merge_range("I9:I10", 'PAX \n ركاب', cell_text_format)
        worksheet.merge_range("J9:J10", '', )
        worksheet.merge_range("K9:K10", 'FLTS \n رحلات', cell_text_format)
        worksheet.merge_range("L9:L10", 'PAX \n ركاب', cell_text_format)
        worksheet.merge_range("M9:M10", 'FLTS \n رحلات', cell_text_format)
        worksheet.merge_range("N9:N10", 'PAX \n ركاب', cell_text_format)
        worksheet.merge_range("O9:O10", 'FLTS \n رحلات', cell_text_format)
        worksheet.merge_range("P9:P10", 'PAX \n ركاب', cell_text_format)
        worksheet.merge_range("Q9:Q10", 'FLTS \n رحلات', cell_text_format)
        worksheet.merge_range("R9:R10", 'PAX \n ركاب', cell_text_format)


        def daterange(start_date, end_date):
            for n in range(int((end_date - start_date).days) + 1):
                yield start_date + timedelta(n)
        row = 9
        ams_data = self.env['ams.data']

        tota_flight_all = 0
        tota_pax_all = 0
        g_a_terminal_haj = 0
        g_a_terminal_haj_pax = 0
        g_a_terminal_north = 0
        g_a_terminal_north_pax = 0
        g_a_terminal_south = 0
        g_a_terminal_south_pax = 0
        g_a_total_flight = 0
        g_a_total_pax = 0

        g_d_terminal_haj = 0
        g_d_terminal_haj_pax = 0
        g_d_terminal_north = 0
        g_d_terminal_north_pax = 0
        g_d_terminal_south = 0
        g_d_terminal_south_pax = 0
        g_d_total_flight = 0
        g_d_total_pax = 0

        a_terminal_haj_weekly = 0
        a_terminal_haj_pax_weekly = 0
        a_terminal_north_weekly = 0
        a_terminal_north_pax_weekly = 0
        a_terminal_south_weekly = 0
        a_terminal_south_pax_weekly = 0
        a_terminal_total_flight_weekly = 0
        a_terminal_total_pax_weekly = 0

        d_terminal_haj_weekly = 0
        d_terminal_haj_pax_weekly = 0
        d_terminal_north_weekly = 0
        d_terminal_north_pax_weekly = 0
        d_terminal_south_weekly = 0
        d_terminal_south_pax_weekly = 0
        d_terminal_total_flight_weekly = 0
        d_terminal_total_pax_weekly = 0

        for single_date in daterange(from_date.date(), to_date.date()):
            row += 1
            a_terminal_haj = 0
            a_terminal_haj_pax = 0
            a_terminal_north = 0
            a_terminal_north_pax = 0
            a_terminal_south = 0
            a_terminal_south_pax = 0
            a_total_flight = 0
            a_total_pax = 0

            d_terminal_haj = 0
            d_terminal_haj_pax = 0
            d_terminal_north = 0
            d_terminal_north_pax = 0
            d_terminal_south = 0
            d_terminal_south_pax = 0
            d_total_flight = 0
            d_total_pax = 0
            date_data = ams_data.search([('actual_a_time_date', '=', single_date)])
            for rec in date_data:
                if rec.a_terminal == 'H':
                    a_terminal_haj +=1
                    a_terminal_haj_pax += rec.a_passenger_no

                elif rec.a_terminal == 'N':
                    a_terminal_north += 1
                    a_terminal_north_pax += rec.a_passenger_no

                elif rec.a_terminal == 'S':
                    a_terminal_south += 1
                    a_terminal_south_pax += rec.a_passenger_no

                a_total_flight = a_terminal_haj + a_terminal_north + a_terminal_south
                a_total_pax = a_terminal_haj_pax + a_terminal_north_pax + a_terminal_south_pax

                if rec.d_terminal == 'H':
                    d_terminal_haj +=1
                    d_terminal_haj_pax += rec.d_passenger_no

                elif rec.d_terminal == 'N':
                    d_terminal_north += 1
                    d_terminal_north_pax += rec.d_passenger_no

                elif rec.d_terminal == 'S':
                    d_terminal_south += 1
                    d_terminal_south_pax += rec.d_passenger_no

                d_total_flight = d_terminal_haj + d_terminal_north + d_terminal_south
                d_total_pax = d_terminal_haj_pax + d_terminal_north_pax + d_terminal_south_pax

            worksheet.write(row, col + 1, str(single_date), cell_text_format_values)
            worksheet.write(row, col + 2, str(a_terminal_haj), cell_text_format_values)
            a_terminal_haj_weekly += a_terminal_haj
            worksheet.write(row, col + 3, str(a_terminal_haj_pax), cell_text_format_values)
            a_terminal_haj_pax_weekly += a_terminal_haj_pax
            worksheet.write(row, col + 4, str(a_terminal_north), cell_text_format_values)
            a_terminal_north_weekly += a_terminal_north
            worksheet.write(row, col + 5, str(a_terminal_north_pax), cell_text_format_values)
            a_terminal_north_pax_weekly += a_terminal_north_pax
            worksheet.write(row, col + 6, str(a_terminal_south),cell_text_format_values)
            a_terminal_south_weekly += a_terminal_south
            worksheet.write(row, col + 7, str(a_terminal_south_pax),cell_text_format_values)
            a_terminal_south_pax_weekly += a_terminal_south_pax
            worksheet.write(row, col + 8, str(a_total_flight), cell_text_format_values)
            a_terminal_total_flight_weekly += a_total_flight
            worksheet.write(row, col + 9, str(a_total_pax), cell_text_format_values)
            a_terminal_total_pax_weekly += a_total_pax

            worksheet.write(row, col + 11, str(d_terminal_haj),cell_text_format_values)
            d_terminal_haj_weekly += d_terminal_haj
            worksheet.write(row, col + 12, str(d_terminal_haj_pax),cell_text_format_values)
            d_terminal_haj_pax_weekly += d_terminal_haj_pax
            worksheet.write(row, col + 13, str(d_terminal_north),cell_text_format_values)
            d_terminal_north_weekly += d_terminal_north
            worksheet.write(row, col + 14, str(d_terminal_north_pax),cell_text_format_values)
            d_terminal_north_pax_weekly += d_terminal_north_pax
            worksheet.write(row, col + 15, str(d_terminal_south),cell_text_format_values)
            d_terminal_south_weekly += d_terminal_south
            worksheet.write(row, col + 16, str(d_terminal_south_pax),cell_text_format_values)
            d_terminal_south_pax_weekly += d_terminal_south_pax
            worksheet.write(row, col + 17, str(d_total_flight),cell_text_format_values)
            d_terminal_total_flight_weekly += d_total_flight
            worksheet.write(row, col + 18, str(d_total_pax),cell_text_format_values)
            d_terminal_total_pax_weekly += d_total_pax


            if single_date.strftime('%A') == 'Thursday':
                row += 1
                worksheet.write(row, col + 1, str('WEEKLY TTL'), cell_text_format)
                worksheet.write(row, col + 2, str(a_terminal_haj_weekly), cell_text_format)
                worksheet.write(row, col + 3, str(a_terminal_haj_pax_weekly), cell_text_format)
                worksheet.write(row, col + 4, str(a_terminal_north_weekly), cell_text_format)
                worksheet.write(row, col + 5, str(a_terminal_north_pax_weekly), cell_text_format)
                worksheet.write(row, col + 6, str(a_terminal_south_weekly), cell_text_format)
                worksheet.write(row, col + 7, str(a_terminal_south_pax_weekly), cell_text_format)
                worksheet.write(row, col + 8, str(a_terminal_total_flight_weekly), cell_text_format)
                worksheet.write(row, col + 9, str(a_terminal_total_pax_weekly), cell_text_format)

                worksheet.write(row, col + 11, str(d_terminal_haj_weekly), cell_text_format)
                worksheet.write(row, col + 12, str(d_terminal_haj_pax_weekly), cell_text_format)
                worksheet.write(row, col + 13, str(d_terminal_north_weekly), cell_text_format)
                worksheet.write(row, col + 14, str(d_terminal_north_pax_weekly), cell_text_format)
                worksheet.write(row, col + 15, str(d_terminal_south_weekly), cell_text_format)
                worksheet.write(row, col + 16, str(d_terminal_south_pax_weekly), cell_text_format)
                worksheet.write(row, col + 17, str(d_terminal_total_flight_weekly), cell_text_format)
                worksheet.write(row, col + 18, str(d_terminal_total_pax_weekly), cell_text_format)
                a_terminal_haj_weekly = 0
                a_terminal_haj_pax_weekly = 0
                a_terminal_north_weekly = 0
                a_terminal_north_pax_weekly = 0
                a_terminal_south_weekly = 0
                a_terminal_south_pax_weekly = 0
                a_terminal_total_flight_weekly = 0
                a_terminal_total_pax_weekly = 0

                d_terminal_haj_weekly = 0
                d_terminal_haj_pax_weekly = 0
                d_terminal_north_weekly = 0
                d_terminal_north_pax_weekly = 0
                d_terminal_south_weekly = 0
                d_terminal_south_pax_weekly = 0
                d_terminal_total_flight_weekly = 0
                d_terminal_total_pax_weekly = 0


            g_a_terminal_haj += a_terminal_haj
            g_a_terminal_haj_pax += a_terminal_haj_pax
            g_a_terminal_north += a_terminal_north
            g_a_terminal_north_pax += a_terminal_north_pax
            g_a_terminal_south += a_terminal_south
            g_a_terminal_south_pax += a_terminal_south_pax
            g_a_total_flight += a_total_flight
            g_a_total_pax += a_total_pax

            g_d_terminal_haj += d_terminal_haj
            g_d_terminal_haj_pax += d_terminal_haj_pax
            g_d_terminal_north += d_terminal_north
            g_d_terminal_north_pax += d_terminal_north_pax
            g_d_terminal_south += d_terminal_south
            g_d_terminal_south_pax += d_terminal_south_pax
            g_d_total_flight += d_total_flight
            g_d_total_pax += d_total_pax

            # Totals
        row +=1
        worksheet.write(row, col + 1, str('Grand Total'), cell_text_format)
        worksheet.write(row, col + 2, str(g_a_terminal_haj), cell_text_format)
        worksheet.write(row, col + 3, str(g_a_terminal_haj_pax), cell_text_format)
        worksheet.write(row, col + 4, str(g_a_terminal_north), cell_text_format)
        worksheet.write(row, col + 5, str(g_a_terminal_north_pax), cell_text_format)
        worksheet.write(row, col + 6, str(g_a_terminal_south), cell_text_format)
        worksheet.write(row, col + 7, str(g_a_terminal_south_pax), cell_text_format)
        worksheet.write(row, col + 8, str(g_a_total_flight), cell_text_format)
        worksheet.write(row, col + 9, str(g_a_total_pax), cell_text_format)
        worksheet.write(row, col + 10, str(''), )
        worksheet.write(row, col + 11, str(g_d_terminal_haj), cell_text_format)
        worksheet.write(row, col + 12, str(g_d_terminal_haj_pax), cell_text_format)
        worksheet.write(row, col + 13, str(g_d_terminal_north), cell_text_format)
        worksheet.write(row, col + 14, str(g_d_terminal_north_pax), cell_text_format)
        worksheet.write(row, col + 15, str(g_d_terminal_south), cell_text_format)
        worksheet.write(row, col + 16, str(g_d_terminal_south_pax), cell_text_format)
        worksheet.write(row, col + 17, str(g_d_total_flight), cell_text_format)
        worksheet.write(row, col + 18, str(g_d_total_pax), cell_text_format)
        row +=3
        worksheet.merge_range("O%s:P%s" % (row+1,row+1), 'Total Flights',cell_text_format)
        worksheet.merge_range("Q%s:R%s" % (row+1,row+1), str(g_d_total_flight + g_a_total_flight),cell_text_format)
        worksheet.merge_range("O%s:P%s" % (row+2,row+2), 'Total PAX',cell_text_format)
        worksheet.merge_range("Q%s:R%s" % (row+2,row+2), str(g_d_total_pax + g_a_total_pax),cell_text_format)

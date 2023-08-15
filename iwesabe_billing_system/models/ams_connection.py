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
from odoo import models, fields
from odoo.exceptions import UserError
try:
    import pymssql
except:
    pass


class AmsBillingInstance(models.Model):
    _name = 'ams.billing.instance'

    name = fields.Char('Name', required=True)
    server = fields.Char('Server', required=True)
    database_name = fields.Char('Database Name', required=True)
    user = fields.Char('User', required=True)
    password = fields.Char('Password', required=True)
    gaca_tbc = fields.Float(string="GACA TBC",  required=False, )

    def check_connection(self, raise_if_succeded=True):
        try:
            conn = pymssql.connect(
                server=self.server.strip(),
                user=self.user.strip(),
                password=self.password,
                database=self.database_name.strip()
            )

            if conn and raise_if_succeded:
                raise UserError("Connection Succeeded.")

        except Exception as e:
            raise UserError(e.args[0])

    def get_all_data(self, date_from, date_to):
        self.ensure_one()
        conn = pymssql.connect(
            server=self.server.strip(),
            user=self.user.strip(),
            password=self.password,
            database=self.database_name.strip()
        )

        cursor = conn.cursor()
        # just for checking purpose
        # query = """SELECT * FROM ams_view where ATD>= %s AND ATD <= %s """
        # cursor.execute(query, (date_from, date_to))
        # rows = cursor.fetchall()
        # print ("rows", rows)
        # cursor.execute("SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS  where table_name='ams_view';")

        query = """
        SELECT ID, ARPRT, AFLTNO, DFLTNO, AACT, ACAT,
            APRON,REGNO,AMTOW,AGHA,ASTAT,DSTAT,ATMNL,
            DTRMNL,ATA,ATD,ATD2,APAX,DPAX,ASTND,DSTND,
            HN,DHN,FRM,DTo,ABUSS,DBUSS,CheckIn_counter,
            AFLT_type,DFLT_type,AAIRL,DAIRL
        FROM ams_view
        where ATD>= %s AND ATD <= %s """

        cursor.execute(query, (date_from, date_to))

        rows = cursor.fetchall()

        data = []
        for row in rows:
            ams_id = row[0]
            airline = row[1]
            arrival_flight_no = row[2]
            departure_flight_no = row[3]
            actual_aircraft = row[4]
            actual_category = row[5]
            apron = row[6]
            reg_no = row[7]
            amtow = row[8]
            agha = row[9]
            a_status = row[10]
            d_status = row[11]
            a_terminal = row[12]
            d_terminal = row[13]
            actual_a_time = row[14]
            actual_d_time = row[15]
            ADT2 = row[16]
            a_passenger_no = row[17]
            d_passenger_no = row[18]
            a_stand = row[19]
            d_stand = row[20]
            HN = row[21]
            DHN = row[22]
            from_city = row[23]
            to_city = row[24]
            ABUSS = row[25]
            DBUSS = row[26]
            check_in_counter = row[27]
            AFLT_type = row[28]
            DFLT_type = row[29]
            AAIRL = row[30]
            DAIRL = row[31]

            data.append({
                'ams_id': ams_id,
                'airline': airline,
                'arrival_flight_no': arrival_flight_no,
                'departure_flight_no': departure_flight_no,
                'actual_aircraft': actual_aircraft,
                'actual_category': actual_category,
                'apron': apron,
                'reg_no': reg_no,
                'amtow': amtow,
                'agha': agha,
                'a_status': a_status,
                'd_status': d_status,
                'a_terminal': a_terminal,
                'd_terminal': d_terminal,
                'actual_a_time': actual_a_time,
                'actual_d_time': actual_d_time,
                'ADT2': ADT2,
                'a_passenger_no': a_passenger_no,
                'd_passenger_no': d_passenger_no,
                'a_stand': a_stand,
                'd_stand': d_stand,
                'HN': HN,
                'DHN': DHN,
                'from_city': from_city,
                'to_city': to_city,
                'ABUSS': ABUSS,
                'DBUSS': DBUSS,
                'check_in_counter': check_in_counter,
                'AFLT_type': AFLT_type,
                'DFLT_type': DFLT_type,
                'arrival_airline': AAIRL,
                'departure_airline': DAIRL
            })
        return data

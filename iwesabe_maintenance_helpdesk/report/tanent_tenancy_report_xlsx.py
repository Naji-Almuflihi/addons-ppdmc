 # -*- coding: utf-8 -*-
from odoo.http import request
from odoo import models, api,fields
from datetime import date,datetime
from odoo.exceptions import UserError, ValidationError


from datetime import datetime, timedelta



class tanent_tenancy_reportXls(models.AbstractModel):
    _name = 'report.iwesabe_maintenance_helpdesk.tanent_tenancy_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        name =  data['form']
        worksheet = workbook.add_worksheet("Tenant Tenancy Annual Increase Report")
        # worksheet.right_to_left()
        f1 = workbook.add_format({'bold': True, 'font_color': '#000000', 'border': False, 'align': 'vcenter','num_format': '#,##0.00'})
        f2 = workbook.add_format({'bold': True, 'font_color': '#000000', 'border': False, 'align': 'center','num_format': '#,##0.00','fg_color': 'DCDCDC',})
        cell_text_format = workbook.add_format({'align': 'center',
                                                'bold': True,
                                                'border': 2,
                                                'size': 12,
                                                'fg_color': '#e0bdba',

                                                'num_format': '#,##0.00'
                                                })
        cell_text_format_values = workbook.add_format({'align': 'center',
                                                       'bold': False,
                                                       'border': 2,
                                                       'size': 10,
                                                       'fg_color': 'E0FFFF',
                                                       'num_format': '#,##0.00'
                                                               })
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('C:C', 25)
        worksheet.set_column('D:D', 25)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 8)
        worksheet.set_column('H:H', 8)
        worksheet.set_column('I:I', 8)
        worksheet.set_column('J:J', 8)
        worksheet.set_column('K:K', 15)
        worksheet.set_column('L:L', 15)

        row = 0
        col = -1
        worksheet.write(row + 2, col + 1,
                        'Report For Tenant Tenancy Expected Rent', f1)

        worksheet.write(row + 5, col + 1, 'Tenant Tenancy No', cell_text_format)
        worksheet.write(row + 5, col + 2, 'Customer Name', cell_text_format)
        worksheet.write(row + 5, col + 3, 'Current Rent', cell_text_format)
        worksheet.write(row + 5, col + 4, 'Annual Increase Rate (%)', cell_text_format)
        worksheet.write(row + 5, col + 5, 'Expected Rent', cell_text_format)
        row = 6
        seq = 0
        tenant_tenancy = self.env['tenant.tenancy'].search([('state','=','open')])
        total_rent = 0.0
        total_rent_expected = 0.0

        for tenant in tenant_tenancy:

            row += 1
            seq += 1
            worksheet.write(row, col + 1, str(tenant.name), cell_text_format_values)
            worksheet.write(row, col + 2, str(tenant.tenant_id.name or ''), cell_text_format_values)
            worksheet.write(row, col + 3, str(tenant.total_rent or ' '), cell_text_format_values)
            total_rent += tenant.total_rent
            worksheet.write(row, col + 4, str(tenant.annual_rate), cell_text_format_values)
            worksheet.write(row, col + 5, str(tenant.total_rent + (tenant.total_rent * tenant.annual_rate / 100)), cell_text_format_values)
            total_rent_expected += tenant.total_rent + (tenant.total_rent * tenant.annual_rate / 100)

        row +=1
        worksheet.write(row, col + 1, str('Total'), f2)
        worksheet.write(row, col + 3, str(round(total_rent,2)), f2)
        worksheet.write(row, col + 5, str(round(total_rent_expected,2)), f2)

        row = 4
        # worksheet.write(row, col + 1, str('Total'), cell_text_format_values)
        worksheet.write(row, col + 3, str(round(total_rent,2)), f2)
        worksheet.write(row, col + 5, str(round(total_rent_expected,2)), f2)



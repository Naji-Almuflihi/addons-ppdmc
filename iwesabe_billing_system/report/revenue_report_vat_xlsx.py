# -*- coding: utf-8 -*-
from odoo import models


class revenue_repor_VattXls(models.AbstractModel):
    _name = 'report.iwesabe_billing_system.revenue_report_vat_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet("Revenue Report With Vat")
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
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 10)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 10)
        worksheet.set_column('F:F', 10)
        worksheet.set_column('G:G', 10)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 15)
        worksheet.set_column('J:J', 10)
        worksheet.set_column('K:K', 12)
        worksheet.set_column('L:L', 10)
        worksheet.set_column('M:M', 10)
        worksheet.set_column('N:N', 8)
        worksheet.set_column('O:O', 8)
        worksheet.set_column('P:P', 8)
        worksheet.set_column('Q:Q', 8)
        worksheet.set_column('R:R', 8)
        worksheet.set_column('S:S', 10)
        worksheet.set_column('T:T', 18)
        worksheet.set_column('U:U', 10)
        worksheet.set_column('V:V', 8)
        worksheet.set_column('W:W', 10)
        worksheet.set_column('X:X', 18)
        worksheet.set_column('Y:Y', 12)
        worksheet.set_column('Z:Z', 8)

        row = 0
        col = -1
        if lines.with_vat:
            worksheet.merge_range('A3:E3', 'Report For Revenue With Vat From ' + str(lines.from_date) + ' To ' + str(lines.to_date), f1)
        else:
            worksheet.merge_range('A3:E3', 'Report For Revenue Without Vat From ' + str(lines.from_date) + ' To ' + str(lines.to_date), f1)

        worksheet.write(row + 11, col + 1, '#', cell_text_format)
        worksheet.write(row + 11, col + 2, 'Name', cell_text_format)
        worksheet.write(row + 11, col + 3, 'TBC', cell_text_format)
        worksheet.write(row + 11, col + 4, 'Terminal Facilities Utilization', cell_text_format)
        worksheet.write(row + 11, col + 5, 'systems', cell_text_format)
        worksheet.write(row + 11, col + 6, '400hz', cell_text_format)
        worksheet.write(row + 11, col + 7, 'Ground Handling', cell_text_format)
        worksheet.write(row + 11, col + 8, 'Aircraft Parking Not Registered', cell_text_format)
        worksheet.write(row + 11, col + 9, 'Aircraft Registered', cell_text_format)
        worksheet.write(row + 11, col + 10, 'PBB Fees', cell_text_format)
        worksheet.write(row + 11, col + 11, 'Security Charge', cell_text_format)
        worksheet.write(row + 11, col + 12, 'Total', cell_text_format)
        row = 12
        seq = 0
        invoice_appendix = self.env['invoice.appendix'].search([('from_date', '>=', lines.from_date), ('to_date', '<=', lines.to_date)])
        partners = invoice_appendix.mapped('partner_id')
        term_faciliti_column_total = 0.0
        systems_column_total = 0.0
        field_400_hz_column_total = 0.0
        ground_handling_column_total = 0.0
        aircraft_parking_not_registered_column_total = 0.0
        aircraft_registered_column_total = 0.0
        plb_busses_column_total = 0.0
        security_services_column_total = 0.0
        fees_total_column_total = 0.0
        gaca_column_total = 0.0
        gaca_tpc = 0.0
        for tpc in self.env['ams.billing.instance'].search([]):
            gaca_tpc = tpc.gaca_tbc
        for part in partners:
            gaca_tbc_total = 0.0
            term_facilities_utilization_total = 0.0
            systems_total = 0.0
            field_400_hz_total = 0.0
            ground_handling_total = 0.0
            aircraft_parking_not_registered_total = 0.0
            aircraft_registered_total = 0.0
            plb_busses_total = 0.0
            security_services_total = 0.0
            fees_total_total = 0.0
            appendix_partner = self.env['invoice.appendix'].search([('from_date', '>=', lines.from_date), ('to_date', '<=', lines.to_date), ('partner_id', '=', part.id)])

            for app_part in appendix_partner:
                if lines.with_vat:
                    gaca_tbc_total += sum(app_part.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('pax')) * gaca_tpc if gaca_tpc else sum(app_part.invoice_appendix_line_ids.mapped('pax'))
                    term_facilities_utilization_total += sum(app_part.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('term_facilities_utilization'))
                    systems_total += sum(app_part.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('systems'))
                    field_400_hz_total += sum(app_part.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('field_400_hz'))
                    ground_handling_total += sum(app_part.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('ground_handling'))
                    aircraft_parking_not_registered_total += sum(app_part.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('aircraft_parking_not_registered'))
                    aircraft_registered_total += sum(app_part.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('aircraft_registered'))
                    plb_busses_total += sum(app_part.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('plb_busses'))
                    security_services_total += sum(app_part.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('security_services'))
                    fees_total_total += sum(app_part.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'I').mapped('fees_total'))
                else:
                    gaca_tbc_total += sum(
                        app_part.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped(
                            'pax')) * gaca_tpc if gaca_tpc else sum(app_part.invoice_appendix_line_ids.mapped('pax'))
                    term_facilities_utilization_total += sum(
                        app_part.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped(
                            'term_facilities_utilization'))
                    systems_total += sum(
                        app_part.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('systems'))
                    field_400_hz_total += sum(
                        app_part.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('field_400_hz'))
                    ground_handling_total += sum(
                        app_part.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped(
                            'ground_handling'))
                    aircraft_parking_not_registered_total += sum(
                        app_part.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped(
                            'aircraft_parking_not_registered'))
                    aircraft_registered_total += sum(
                        app_part.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped(
                            'aircraft_registered'))
                    plb_busses_total += sum(
                        app_part.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('plb_busses'))
                    security_services_total += sum(
                        app_part.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped(
                            'security_services'))
                    fees_total_total += sum(
                        app_part.invoice_appendix_line_ids.filtered(lambda x: x.FLT_type == 'D').mapped('fees_total'))

            row += 1
            seq += 1
            worksheet.write(row, col + 1, str(seq), cell_text_format_values)
            worksheet.write(row, col + 2, str(part.name), cell_text_format_values)
            worksheet.write(row, col + 3, gaca_tbc_total, cell_text_format_values)
            gaca_column_total += gaca_tbc_total
            worksheet.write(row, col + 4, term_facilities_utilization_total, cell_text_format_values)
            term_faciliti_column_total += term_facilities_utilization_total
            worksheet.write(row, col + 5, systems_total, cell_text_format_values)
            systems_column_total += systems_total
            worksheet.write(row, col + 6, field_400_hz_total, cell_text_format_values)
            field_400_hz_column_total += field_400_hz_total
            worksheet.write(row, col + 7, ground_handling_total, cell_text_format_values)
            ground_handling_column_total += ground_handling_total
            worksheet.write(row, col + 8, aircraft_parking_not_registered_total, cell_text_format_values)
            aircraft_parking_not_registered_column_total += aircraft_parking_not_registered_total
            worksheet.write(row, col + 9, aircraft_registered_total, cell_text_format_values)
            aircraft_registered_column_total += aircraft_registered_total
            worksheet.write(row, col + 10, plb_busses_total, cell_text_format_values)
            plb_busses_column_total += plb_busses_total
            worksheet.write(row, col + 11, security_services_total, cell_text_format_values)
            security_services_column_total += security_services_total
            worksheet.write(row, col + 12, fees_total_total, cell_text_format_values)
            fees_total_column_total += fees_total_total

        row += 1
        worksheet.write(row, col + 2, str('Total'), f2)
        worksheet.write(row, col + 3, round(gaca_column_total, 2), f2)
        worksheet.write(row, col + 4, round(term_faciliti_column_total, 2), f2)
        worksheet.write(row, col + 5, round(systems_column_total, 2), f2)
        worksheet.write(row, col + 6, round(field_400_hz_column_total, 2), f2)
        worksheet.write(row, col + 7, round(ground_handling_column_total, 2), f2)
        worksheet.write(row, col + 8, round(aircraft_parking_not_registered_column_total, 2), f2)
        worksheet.write(row, col + 9, round(aircraft_registered_column_total, 2), f2)
        worksheet.write(row, col + 10, round(plb_busses_column_total, 2), f2)
        worksheet.write(row, col + 11, round(security_services_column_total, 2), f2)
        worksheet.write(row, col + 12, round(fees_total_column_total, 2), f2)

        row = 0
        col = -1

        worksheet.write(row + 5, col + 2, 'Bill To', cell_text_format)
        worksheet.write(row + 5, col + 3, 'TBC', cell_text_format)
        worksheet.write(row + 5, col + 4, 'Terminal Facilities Utilization', cell_text_format)
        worksheet.write(row + 5, col + 5, 'systems', cell_text_format)
        worksheet.write(row + 5, col + 6, '400hz', cell_text_format)
        worksheet.write(row + 5, col + 7, 'Ground Handling', cell_text_format)
        worksheet.write(row + 5, col + 8, 'Aircraft Parking Not Registered', cell_text_format)
        worksheet.write(row + 5, col + 9, 'Aircraft Registered', cell_text_format)
        worksheet.write(row + 5, col + 10, 'PBB Fees', cell_text_format)
        worksheet.write(row + 5, col + 11, 'Security Charge', cell_text_format)
        worksheet.write(row + 5, col + 12, 'Total', cell_text_format)

        row = 6
        worksheet.write(row, col + 2, str('General Authority Of Aviation ( GACA )'), cell_text_format_values)
        worksheet.write(row, col + 3, round(gaca_column_total, 2), cell_text_format_values)
        worksheet.write(row, col + 4, '0.0', cell_text_format_values)
        worksheet.write(row, col + 5, '0.0', cell_text_format_values)
        worksheet.write(row, col + 6, '0.0', cell_text_format_values)
        worksheet.write(row, col + 7, '0.0', cell_text_format_values)
        worksheet.write(row, col + 8, '0.0', cell_text_format_values)
        worksheet.write(row, col + 9, '0.0', cell_text_format_values)
        worksheet.write(row, col + 10, '0.0', cell_text_format_values)
        worksheet.write(row, col + 11, '0.0', cell_text_format_values)
        worksheet.write(row, col + 12, round(gaca_column_total, 2), f2)

        row = 7
        worksheet.write(row, col + 2, str('Airlines'), cell_text_format_values)
        worksheet.write(row, col + 3, '0.0', cell_text_format_values)
        worksheet.write(row, col + 4, round(term_faciliti_column_total, 2), cell_text_format_values)
        worksheet.write(row, col + 5, round(systems_column_total, 2), cell_text_format_values)
        worksheet.write(row, col + 6, round(field_400_hz_column_total, 2), cell_text_format_values)
        worksheet.write(row, col + 7, '0.0', cell_text_format_values)
        worksheet.write(row, col + 8, round(aircraft_parking_not_registered_column_total, 2), cell_text_format_values)
        worksheet.write(row, col + 9, round(aircraft_registered_column_total, 2), cell_text_format_values)
        worksheet.write(row, col + 10, round(plb_busses_column_total, 2), cell_text_format_values)
        worksheet.write(row, col + 11, round(security_services_column_total, 2), cell_text_format_values)
        total_row_2 = round(term_faciliti_column_total, 2) + round(systems_column_total, 2) + round(field_400_hz_column_total, 2) + round(aircraft_parking_not_registered_column_total, 2)
        total_row_2 += round(aircraft_registered_column_total, 2) + round(plb_busses_column_total, 2) + round(security_services_column_total, 2)
        worksheet.write(row, col + 12, round(total_row_2, 2), f2)

        row = 8
        worksheet.write(row, col + 2, str('Handling Agents'), cell_text_format_values)
        worksheet.write(row, col + 3, '0.0', cell_text_format_values)
        worksheet.write(row, col + 4, '0.0', cell_text_format_values)
        worksheet.write(row, col + 5, '0.0', cell_text_format_values)
        worksheet.write(row, col + 6, '0.0', cell_text_format_values)
        worksheet.write(row, col + 7, round(ground_handling_column_total, 2), cell_text_format_values)
        worksheet.write(row, col + 8, '0.0', cell_text_format_values)
        worksheet.write(row, col + 9, '0.0', cell_text_format_values)
        worksheet.write(row, col + 10, '0.0', cell_text_format_values)
        worksheet.write(row, col + 11, '0.0', cell_text_format_values)
        worksheet.write(row, col + 12, round(ground_handling_column_total, 2), f2)

        row = 9
        worksheet.write(row, col + 2, str('Total'), f2)
        worksheet.write(row, col + 3, round(gaca_column_total, 2), f2)
        worksheet.write(row, col + 4, round(term_faciliti_column_total, 2), f2)
        worksheet.write(row, col + 5, round(systems_column_total, 2), f2)
        worksheet.write(row, col + 6, round(field_400_hz_column_total, 2), f2)
        worksheet.write(row, col + 7, round(ground_handling_column_total, 2), f2)
        worksheet.write(row, col + 8, round(aircraft_parking_not_registered_column_total, 2), f2)
        worksheet.write(row, col + 9, round(aircraft_registered_column_total, 2), f2)
        worksheet.write(row, col + 10, round(plb_busses_column_total, 2), f2)
        worksheet.write(row, col + 11, round(security_services_column_total, 2), f2)
        worksheet.write(row, col + 12, round(total_row_2, 2) + round(ground_handling_column_total, 2) + round(gaca_column_total, 2), f2)

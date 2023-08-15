# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF, safe_eval


class revenue_reportVat(models.TransientModel):
    _name = 'wizard.revenue_report.vat'

    from_date = fields.Date(string="From Date", required=False, default=fields.Date.context_today)
    to_date = fields.Date(string="To Date", required=False,)
    with_vat = fields.Boolean(string="With Vat",  )

    def print_revenue_report_vat_xls(self):

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'from_date':self.from_date,
                'to_date':self.to_date,
                'with_vat':self.with_vat,
            },
        }

        return self.env.ref('iwesabe_billing_system.revenue_report_vat_xlsx').report_action(self, data=data)

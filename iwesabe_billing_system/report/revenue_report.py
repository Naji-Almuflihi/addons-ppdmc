# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF, safe_eval


class revenue_report(models.TransientModel):
    _name = 'wizard.revenue_report'

    from_date = fields.Date(string="From Date", required=False, default=fields.Date.context_today)
    to_date = fields.Date(string="To Date", required=False,)

    def print_revenue_report_xls(self):

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'from_date':self.from_date,
                'to_date':self.to_date,
            },
        }

        return self.env.ref('iwesabe_billing_system.revenue_report_xlsx').report_action(self, data=data)

# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF, safe_eval


class flight_movement_report(models.TransientModel):
    _name = 'wizard.flight_movement_report'

    from_date = fields.Datetime(string="From Date", required=False, default=fields.Date.context_today)
    to_date = fields.Datetime(string="To Date", required=False,)

    def print_flight_movement_report_xls(self):

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'from_date':self.from_date,
                'to_date':self.to_date,
            },
        }

        return self.env.ref('iwesabe_billing_system.flight_movement_report_xlsx').report_action(self, data=data)

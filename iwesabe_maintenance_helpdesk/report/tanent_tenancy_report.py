# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF, safe_eval


class tanent_tenancy_report(models.TransientModel):
    _name = 'wizard.tanent_tenancy_report'

    def print_tanent_tenancy_report_xls(self):

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {

            },
        }

        return self.env.ref('iwesabe_maintenance_helpdesk.tanent_tenancy_report_xlsx').report_action(self, data=data)

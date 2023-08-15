from odoo import _, api, fields, models
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class MaintenanceRequestWizard(models.Model):
    _name = 'maintenance.request.wizard'

    note = fields.Text(string='Note')
    maintenance_id = fields.Many2one('maintenance.request', string='Maintenance')

    def note_done(self):
        self.ensure_one()
        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids')
        if active_model == 'maintenance.request':
            active_recs = self.env[active_model].browse(active_ids)
            for rec in active_recs:
                self.maintenance_id.write(
                    {"state": 'in_progress', 'note': self.note})
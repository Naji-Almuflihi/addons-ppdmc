# See LICENSE file for full copyright and licensing details

from datetime import datetime

from odoo.tools import misc
from odoo.exceptions import Warning, ValidationError
from odoo import _, api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class WizardRenewTenancy(models.TransientModel):
    _name = 'renew.tenancy'
    _description = 'Renew Tenancy'

    start_date = fields.Date(
        string='Start Date')
    end_date = fields.Date(
        string='End Date')
    rent_type_id = fields.Many2one(
        comodel_name='rent.type',
        string='Rent Type',
        required=True)

    @api.constrains('start_date', 'end_date')
    def check_date_overlap(self):
        """
        This is a constraint method used to check the from date smaller than
        the Exiration date.
        @param self : object pointer
        """
        for ver in self:
            if ver.start_date and ver.end_date and \
                    ver.end_date < ver.start_date:
                raise ValidationError(_(
                    'End date should be greater than Start Date!'))

    
    def renew_contract(self):
        """
        This Button Method is used to Renew Tenancy.
        @param self: The object pointer
        @return: Dictionary of values.
        """
        context = dict(self._context) or {}
        modid = self.env.ref(
            'iwesabe_ppmdc_airport_management.view_tenant_tenancy_form').id
        if context.get('active_ids', []):
            for rec in self:
                start_d = rec.start_date
                end_d = rec.end_date
               
                if start_d > end_d:
                    raise Warning(
                        _('Please Insert End Date Greater Than Start Date!'))
                act_prop = self.env['tenant.tenancy'].browse(
                    context['active_ids'])
                annual_rate = act_prop.annual_rate
                rent = act_prop.total_rent
                if annual_rate:
                    rent = rent + (rent *annual_rate / 100)
                act_prop.write({
                    'date_start': rec.start_date,
                    'date_end': rec.end_date,
                    'rent_type_id':
                    rec.rent_type_id and rec.rent_type_id.id or False,
                    'state': 'draft',
                    'rent_entry_chck': False,
                    'total_rent': rent
                })
                act_prop.compute_sequence_name_all()
            if self.env.context.get('active_model')=='tenant.tenancy':
                tenancy_record = self.env['tenant.tenancy'].browse(self._context.get('active_ids'))
                tenancy_record.onchange_date_start()
                tenancy_record.onchange_date_end()
                tenancy_record.compute_sequence_name_all()
                for line in tenancy_record.property_ids:
                    line.date_start=self.start_date
                    line.date_end=self.end_date


        return {
            'view_mode': 'form',
            'view_id': modid,
            'view_type': 'form',
            'res_model': 'tenant.tenancy',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': context['active_ids'][0],
        }

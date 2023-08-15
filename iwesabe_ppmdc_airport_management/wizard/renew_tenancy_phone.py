# See LICENSE file for full copyright and licensing details

from datetime import datetime

from odoo.tools import misc
from odoo.exceptions import Warning, ValidationError
from odoo import _, api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class WizardRenewTenancyPhone(models.TransientModel):
    _name = 'renew.tenancy.phone'
    _description = 'Renew Tenancy Phone'

    start_date = fields.Date(
        string='Start Date')
    end_date = fields.Date(
        string='End Date')


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
            'iwesabe_ppmdc_airport_management.tenancy_phone_extention_form').id
        if context.get('active_ids', []):
            for rec in self:
                start_d = rec.start_date
                end_d = rec.end_date
               
                if start_d > end_d:
                    raise Warning(
                        _('Please Insert End Date Greater Than Start Date!'))
                act_prop = self.env['tenancy.phone.extention'].browse(
                    context['active_ids'])
                act_prop.write({
                    'date_start': rec.start_date,
                    'date_end': rec.end_date,
                    'state': 'draft',
                })
        return {
            'view_mode': 'form',
            'view_id': modid,
            'view_type': 'form',
            'res_model': 'tenancy.phone.extention',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': context['active_ids'][0],
        }

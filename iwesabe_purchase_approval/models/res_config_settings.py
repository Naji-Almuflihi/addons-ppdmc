# * coding: utf8 *
##############################################################################
#
#    Global Creative Concepts Tech Co Ltd.
#    Copyright (C) 2018TODAY iWesabe (<http://www.iwesabe.com>).
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

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    second_approval = fields.Boolean(string="Second Approval", related="company_id.second_approval", readonly=False)
    second_approval_minimum_amount = fields.Monetary(string="Minimum Amount",
                                                     related="company_id.second_approval_minimum_amount",
                                                     readonly=False)

    @api.constrains('second_approval_minimum_amount')
    def warrning_seccond_approval(self):
        if self.po_order_approval == True and self.second_approval == True:
            if self.po_double_validation_amount > self.second_approval_minimum_amount:
                raise UserError(_('Second approval amount must be greater than Order approval amount'))

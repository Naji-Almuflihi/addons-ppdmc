from datetime import datetime
from dateutil.relativedelta import relativedelta
import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class AccountAssetAsset(models.Model):
     _inherit = 'account.asset'
     _description = 'Asset'

     property_id = fields.Many2one(
         'property.property',
          string='Property',
     )

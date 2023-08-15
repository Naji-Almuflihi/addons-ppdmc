from openerp import models, fields


class StockLocationInherit(models.Model):
    _inherit = 'stock.location'

    maintenance_team_id = fields.Many2one(comodel_name="maintenance.team", string="SubContractor / Team",)

    _sql_constraints = [('maintenance_team_id', 'UNIQUE (maintenance_team_id)', 'SubContractor / Team  already exists'), ]

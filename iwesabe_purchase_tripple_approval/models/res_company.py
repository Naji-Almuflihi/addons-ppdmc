# -*- coding: utf-8 -*-
##############################################################################
#
#    Global Creative Concepts Tech Co Ltd.
#    Copyright (C) 2018-TODAY iWesabe (<http://www.iwesabe.com>).
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
from odoo import fields, models, api


class Company(models.Model):
    _inherit = 'res.company'

    three_step_validation =  fields.Boolean(
        'Three Step Approval'
    )
    finance_validation_amount = fields.Monetary(
        'Finance Validation Amount',
        default=0.0
    )
    director_validation_amount = fields.Monetary(
        'CEO Validation Amount',
        default=0.0
    )
    email_template_id = fields.Many2one(
        'mail.template',
        string='Purchase Approval Email Template',
    )
    refuse_template_id = fields.Many2one(
        'mail.template',
        string='Purchase Refuse Email Template',
    )


    dept_manager_id = fields.Many2one(
        'res.users',
        string='Purchase Manager',
        domain=lambda self: [("groups_id", "=", self.env.ref( "purchase.group_purchase_manager" ).id)]
    )
    general_manager_id = fields.Many2one(
        'res.users',
        string='Support Service Manager',
        domain=lambda self: [("groups_id", "=", self.env.ref( "iwesabe_purchase_tripple_approval.group_department_manager" ).id)]
    )
    finance_manager_id = fields.Many2one(
        'res.users',
        string='Finance Manager',
        domain=lambda self: [("groups_id", "=", self.env.ref( "iwesabe_purchase_tripple_approval.group_approval_manager" ).id)]
    )
    director_manager_id = fields.Many2one(
        'res.users',
        string='CEO',
        domain=lambda self: [("groups_id", "=", self.env.ref( "iwesabe_purchase_tripple_approval.group_purchase_director" ).id)]
    )
    budget_manager_id = fields.Many2one(
        'res.users',
        string='Review Budget Manager',
        domain=lambda self: [("groups_id", "=", self.env.ref( "iwesabe_purchase_tripple_approval.group_review_budget_manager" ).id)]
    )
    contract_manager_id = fields.Many2one(
        'res.users',
        string='Contract Manager',

    )

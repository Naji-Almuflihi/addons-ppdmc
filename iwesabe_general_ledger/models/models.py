# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class iwesabe_general_ledger(models.Model):
#     _name = 'iwesabe_general_ledger.iwesabe_general_ledger'
#     _description = 'iwesabe_general_ledger.iwesabe_general_ledger'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

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
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    user_item_type = fields.Char(string="User Item Type")
    default_code = fields.Char(string="Internal Reference",  compute="set_internal_reference", store=True, readonly=False)

    @api.onchange('categ_id')
    def _onchange_category_id(self):
        if self.categ_id:
            self.default_code = False
            self.default_code = self.categ_id.complete_code

    @api.depends('categ_id')
    def set_internal_reference(self):
        for res in self:
            if res.categ_id:
                res.categ_id.compute_complete_code()
            if res.categ_id and res.categ_id.complete_code:
                res.default_code = res.categ_id.complete_code


class ProductCategory1(models.Model):
    _inherit = 'product.category'

    @api.depends('parent_id')
    def get_category_is_parent(self):
        for rec in self:
            if rec.parent_id:
                rec.is_parent = True
            else:
                rec.is_parent = False

    @api.depends('name', 'code', 'parent_id', 'product_count', 'parent_id.code', 'child_id')
    @api.onchange('name', 'code', 'parent_id', 'product_count', 'parent_id.code', 'child_id')
    def compute_complete_code(self):
        for category in self:
            for sub_categ_id in category.search([('id', 'child_of', category.ids)]):
                if sub_categ_id.parent_id:
                    old_data = sub_categ_id.parent_id.complete_code.split("/")
                    del old_data[-1]
                    old_d = '/'.join(old_data)
                    if not old_d:
                        sub_categ_id.complete_code = '%s / %s' % (sub_categ_id.code, sub_categ_id.product_count)
                    else:
                        sub_categ_id.complete_code = '%s / %s / %s' % (old_d.strip(), sub_categ_id.code, sub_categ_id.product_count)
                else:
                    sub_categ_id.complete_code = '%s / %s ' % (sub_categ_id.code, sub_categ_id.product_count)
                for pro in self.env['product.template'].search([('categ_id', '=', sub_categ_id.id)]):
                    pro.default_code = sub_categ_id.complete_code

    complete_code = fields.Char('Complete Code', compute='compute_complete_code', store=True)

    code = fields.Char(string="Code")
    code_parent = fields.Char(string="Parent Code")
    is_parent = fields.Boolean(string="Is Parent", compute="get_category_is_parent")

    @api.constrains('code')
    @api.onchange('code')
    def set_code_constrains(self):
        for rec in self:
            if rec.code and len(rec.code) > 4:
                raise UserError(_("Code must be 4 digits only."))

    @api.constrains('code_parent')
    @api.onchange('code_parent')
    def set_code_parent_constrains(self):
        for rec in self:
            if rec.code_parent and len(rec.code_parent) > 2:
                raise UserError(_("Code must be 2 digits only."))

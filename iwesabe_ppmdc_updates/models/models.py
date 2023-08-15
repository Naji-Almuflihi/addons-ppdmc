# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    supplier_site_ids = fields.Many2many("site.solution", string="Supplier Site Solution")


class Purchase(models.Model):
    _inherit = 'purchase.order'

    payment_term_id = fields.Many2one('account.payment.term', 'Payment Terms', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", required=True)


class Product(models.Model):
    _inherit = 'product.template'

    supplier_site_id = fields.Many2one("site.solution", string="Supplier Site Solution", required=False, )

    @api.model
    def get_email_to(self):
        email_list = []
        user_group = self.env.ref(
            "account.group_account_user")
        email_list = [
            usr.partner_id.email for usr in user_group.users if
            usr.partner_id.email]
        print(email_list)
        return ",".join(email_list)

    @api.model
    def create(self, values):
        res = super(Product, self).create(values)
        template_id = self.env.ref('iwesabe_ppmdc_updates.template_mail_create_new_product').id
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(res.id, force_send=True)
        return res


class Payment(models.Model):
    _inherit = 'account.payment'

    invoices_id = fields.Many2one("account.move", string="Invoices", required=False, )
    bills_id = fields.Many2one("account.move", string="Bills", required=False, )
    supplier_site_id = fields.Many2one("site.solution", string="Supplier Site Solution", required=False, )


class AccountSupplier(models.Model):
    _inherit = 'account.move'

    supplier_site_id = fields.Many2one("site.solution", string="Supplier Site Solution", required=False, readonly=True, states={'draft': [('readonly', False)]})

    @api.onchange('partner_id')
    def filter_supplier_site(self):
        return {'domain': {'supplier_site_id': [('id', 'in', self.partner_id.supplier_site_ids.ids)]}}


class AccountLine(models.Model):
    _inherit = 'account.move.line'

    supplier_site_id = fields.Many2one(string="Supplier Site Solution", related="move_id.supplier_site_id", )
    is_vendor = fields.Boolean(string="Vendor?", compute="compute_is_vendor")

    def compute_is_vendor(self):
        for rec in self:
            if rec.is_vendor or not rec.is_vendor:
                if rec.move_id.move_type in ['out_invoice', 'out_refund']:
                    rec.is_vendor = True


class ProductSupplier(models.Model):
    _inherit = 'product.category'

    supplier_site_id = fields.Many2one("site.solution", string="Supplier Site Solution", required=False, )


class NewModuleLine(models.Model):
    _inherit = 'contract.line'

    tax_ids = fields.Many2many("account.tax", string="Taxes", )
    price_total = fields.Float(
        compute="_compute_price_subtotal",
        digits="Account",
        string="Total",
    )

    @api.depends("quantity", "price_unit", "discount", "tax_ids")
    def _compute_price_subtotal(self):
        super(NewModuleLine, self)._compute_price_subtotal()
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_ids.compute_all(price, line.contract_id.pricelist_id.currency_id, line.quantity,
                                             product=line.product_id)
            line.update({
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })



class ContractAbstractContractLine(models.AbstractModel):
    _inherit = "contract.abstract.contract.line"

    tax_ids = fields.Many2many("account.tax", string="Taxes", )

    # @api.depends("quantity", "price_unit", "discount","tax_ids")
    # def _compute_price_subtotal(self):
    #     for line in self:
    #         if line.tax_ids:
    #             subtotal = line.quantity * line.price_unit * line.tax_ids.amount
    #             discount = line.discount / 100
    #             subtotal *= 1 - discount
    #         if not line.tax_ids:
    #             subtotal = line.quantity * line.price_unit
    #             discount = line.discount / 100
    #             subtotal *= 1 - discount
    #         if line.contract_id.pricelist_id:
    #             cur = line.contract_id.pricelist_id.currency_id
    #             line.price_subtotal = cur.round(subtotal)
    #         else:
    #             line.price_subtotal = subtotal


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    # @api.constrains('state')
    # def check_ir_attachment(self):
    #     for rec in self:
    #         list=self.env['ir.attachment'].search([('res_model', '=','hr.expense'),
    #                        ('res_id', '=', rec.id)])
    #         if not list and rec.state == "reported":
    #             raise UserError(_("Please upload document for this record."))


class PropertyNew(models.Model):
    _inherit = 'property.property'

    reason_rent = fields.Char(string="Rent Reason", )

    reason_rent = fields.Many2one(related="rent_price_ids.rent_type_id", required=True, string='Season Rent',)

    def reason_open(self):
        pass


class HrExpenseSheetInherit(models.Model):
    _inherit = 'hr.expense.sheet'
    attachment_number = fields.Integer(compute='_compute_attachment_number', string='Number of Attachments')

    @api.depends('name')
    def _compute_attachment_number(self):
        for sheet in self:
            total = 0
            total = len(self.env['ir.attachment'].search([('res_id', '=', sheet.id), ('res_model', '=', 'hr.expense.sheet')]))
            sheet.attachment_number = total

    def action_get_attachment_view(self):
        res = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        res['domain'] = [('res_model', '=', 'hr.expense.sheet'), ('res_id', '=', self.id)]

        return res

    def action_submit_sheet(self):
        res = super(HrExpenseSheetInherit, self).action_submit_sheet()

        if self.attachment_number == 0:
            raise UserError(_("Please upload document for this record."))

        return res

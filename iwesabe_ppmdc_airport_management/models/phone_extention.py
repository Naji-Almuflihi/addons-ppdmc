# -*- coding:utf-8  -*-
from odoo import fields, models, api


class PhoneExtention(models.Model):
    _name = 'phone.extention'
    _description = "Phone Extention"

    name = fields.Char(string="Name", required=True)
    rent = fields.Float(string="Rent")
    tenancy_phone_id = fields.Many2one('tenancy.phone.extention', string='Tenancy')
    rented = fields.Boolean(string="Rented", readonly=True)
    extention_number_ids = fields.One2many('phone.extentaion.numbers', 'phone_extention_id', string="Extention Numbers")
    product_id = fields.Many2one('product.template', string="Product")
    _sql_constraints = [('name_uniq', 'unique (name)', 'Phone number must be uniqe !!')]


class PhoneExtentionNumbers(models.Model):
    _name = 'phone.extentaion.numbers'
    _descripton = 'PhoneExtention Numbers'

    name = fields.Char(string="Extention Number", required=True)
    reserverd = fields.Boolean(string='reserverd')
    phone_extention_id = fields.Many2one('phone.extention', string='Phone Extention')
    used_by = fields.Char(string="Used By")
    type = fields.Selection([
        ('direct', 'Direct'),
        ('service', 'Service'),
        # ('satble', 'Satble'),
        ('local', 'Local'),
        ('vlan', 'VLAN')
        ], string="Type")
    tenancy_id = fields.Many2one('tenant.tenancy', string='Tenancy')
    partner_id = fields.Many2one(related='tenancy_id.tenant_id', string='Tenant', store=True)
    service_contract_id = fields.Many2one('tenancy.service.contract', string='Service Contract')
    implementation_application_number_id = fields.Many2one('implementation.service.application', string="Implementation Service Application")

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        type_of_request = self._context.get('type_of_request')
        if type_of_request in ('new', 'replacment'):
            args += [('reserverd', '=', False)]
            recs = self.search(args, limit=limit)
            return recs.name_get()
        if type_of_request == 'cancellation':
            args += [('reserverd', '=', True)]
            recs = self.search(args, limit=limit)
            return recs.name_get()
        return super(PhoneExtentionNumbers, self).name_search(name, args=args, operator='ilike', limit=100)

# class PhoneExtentionInvoice(models.Model):
#     _name = 'phone.extention.invoice'
#     _description = 'Phone Extention Invoice'

#     name = fields.Char("Name", required=True)
#     date_from = fields.Date('Date From', required=True)
#     date_to = fields.Date('Date To', required=True)
#     line_ids = fields.One2many('phone.extention.invoice.line', 'extention_invoice_id')

#     tenancy_id = fields.Many2one("tenant.tenancy", string="Tenancy Contract")
#     tenancy_contract_id = fields.Many2one("tenant.tenancy", string="Tenancy Service ")
#     implementation_service_application_id = fields.Many2one("implementation.service.application", string="Implementation Service Application")
#     partner_id = fields.Many2one("res.partner", string="Customer")
#     phone_extention_numbers_ids = fields.Many2many("phone.extentaion.numbers")
#     date = fields.Date(string="Date")

#     invoice_count = fields.Integer(string="Invoice count", compute='_compute_invoice_count')

#     def _compute_invoice_count(self):
#         for rec in self:
#             count = 0
#             for invoice in self.env['account.move'].search([('phone_extention_id', '=', self.id)]):
#                 count += 1
#             rec.invoice_count = count

#     def action_view_invoice(self):
#         return {
#             'name': _('Phone Extention Invoice'),
#             'type': 'ir.actions.act_window',
#             'view_type': 'form',
#             'view_mode': 'tree,form',
#             'res_model': 'account.move',
#             'domain': [('phone_extention_id', '=', self.id)],
#         }

#     def calculate_invoice(self):
#         service_contract_invoice = self.env['service.contract.invoice.line']
#         for rec in self.line_ids:
#             service_contract_invoice.create({
#                 'service_contract_id': rec.extention_number_id.service_contract_id.id,
#                 'name': rec.extention_number_id.name,
#                 'price': rec.price
#             })
#             rec.invoiced = True

#     def create_invoice(self):
#         move_lines = []
#         partner_id = False

#         all_partner = []

#         for line in self.line_ids:
#             partner_id = line.partner_id.id
#             break

#         for line in self.line_ids:
#             all_partner.append(line.partner_id.id)
#             move_lines.append((0, 0, {
#                 'name': "رقم العقد" + str(" - ") + str(line.price),
#                 'quantity': 1,
#                 # 'account_id': self.company_id.service_income_account.id,
#                 'price_unit': line.price,
#             }))

#         for par in all_partner:
#             if par != partner_id:
#                 raise ValidationError(_('Please Set Correct Tenant'))

#         self.env['account.move'].create({
#             'partner_id': self.partner_id.id,
#             'move_type': "out_invoice",
#             'ref': [self.tenancy_id.name+"-"+self.tenancy_contract_id.name]+["-"+str(self.date_from)+"-"+str(self.date_to)],
#             'invoice_line_ids': move_lines,
#             'phone_extention_id': self.id,
#             'invoice_date': self.date,
#         })


# class PhoneExtentionInvoiceLine(models.Model):
#     _name = 'phone.extention.invoice.line'
#     _description = 'Phone Extention Invoice Line'

#     extention_number_id = fields.Many2one('phone.extentaion.numbers', string='Extention Number', required=True)
#     price = fields.Float(string='Price')
#     tenancy_id = fields.Many2one(related='extention_number_id.tenancy_id', string='Tenancy',  store=True)
#     partner_id = fields.Many2one(related='extention_number_id.partner_id', string='Tenant', store=True)
#     extention_invoice_id = fields.Many2one('phone.extention.invoice', string='Extention Invoice')
#     invoiced = fields.Boolean(string='Invoiced', readonly=True)

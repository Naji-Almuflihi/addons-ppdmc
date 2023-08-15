# -*- cosing:utf-8 -*-
from odoo import _, api, fields, models
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    wiz_id =fields.Many2one('maintenance.request.wizard', string='Wiz Id')

    number = fields.Char(string="Number", default=_("New"), readonly=True)
    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket')

    request_date = fields.Datetime('Request Date', tracking=True, default=fields.Date.context_today,
                               help="Date requested for the maintenance to happen")
    department_section_id = fields.Many2one(related='equipment_id.department_id', string="Department/Section Head",)
    user_assistant_id = fields.Many2one("res.users", string="Section Head/Responsible")
    execution_time = fields.Char(string="Execution Times", compute="compute_execution_time_day")
    execution_day = fields.Integer(string="Execution Days", compute='compute_execution_day')
    check_day_time = fields.Boolean()
    is_repair_stage = fields.Boolean(compute="_get_check_stages")
    is_validation_stage = fields.Boolean(compute="_get_check_stages")
    request_validation = fields.Selection(string="Request Validation", selection=[('responsible', 'Section Head/Responsible'), ('supervisor', 'Supervisor Validation'), ])
    is_request_validation = fields.Boolean(compute='check_is_request_validation')

    internal_note = fields.Char()
    subcontract_comment = fields.Char()
    state = fields.Selection(string="", selection=[('draft', 'New Request'), ('submit', 'Submitted'),
                                                   ('in_progress', 'In Repairing'),
                                                   ('under_validation', 'Under Validation'),
                                                   ('repaired', 'Repaired'),
                                                   ], default='draft')

    location_id = fields.Many2one("stock.location", string="Warehouse")
    spare_parts_count = fields.Integer(string="Spare Parts", compute='compute_spare_parts_count')

    module_porperty_zone_id = fields.Many2one("property.zone", string="Module")

    equipment_category_id = fields.Many2one("maintenance.equipment.category", string="Equipment Category")
    system_category_id = fields.Many2one("system.category", string="System Category")
    main_zone_location_id = fields.Many2one("zone.location", string="Main")

    property_id = fields.Many2one(comodel_name="property.property", string="Location Number",)
    property_type_id = fields.Many2one('property.type', string='Location Type / Sub1')
    sub_2 = fields.Char(string="Sub2")

    # user_id = fields.Many2one('res.users', string='Technician', tracking=True, domain=lambda self: [('id', 'in', self.maintenance_team_id.member_ids.ids)])
    # maintenance_team_id

    is_able_to_start = fields.Boolean(string="Start By me", compute="get_my_access")
    is_request_approve = fields.Boolean(string="Is Request Approve", compute="get_access_request_approve")
    is_access_validation = fields.Boolean(string='Is Access Validation', compute="get_access_validation")
    note = fields.Text(string="Reason for return in repair", track_visibility='always')
    is_ask_approve = fields.Boolean(string='Is Ask Approve', compute="get_access_ask_approve")
    closed_date = fields.Datetime('Closed Date')
    actual_duration = fields.Float(compute='_compute_actual_duration', store=True, string="Actual Duration")

    @api.depends('request_date', 'closed_date')
    def _compute_actual_duration(self):
        for res in self:
            res.actual_duration = res._get_duration(res.request_date, res.closed_date)

    def _get_duration(self, request_date, closed_date):
        if not request_date or not closed_date:
            return 0
        dt = closed_date - request_date
        return dt.days * 24 + dt.seconds / 3600

    def get_access_ask_approve(self):
        for res in self:
            res.is_ask_approve = False
            if res.user_id.id == self.env.user.id and res.request_validation == 'supervisor':
                res.is_ask_approve = True


    def get_access_request_approve(self):
        for res in self:
            res.is_request_approve = False
            if res.user_id.id == self.env.user.id and res.request_validation == 'responsible':
                res.is_request_approve = True

    def get_my_access(self):
        for res in self:
            res.is_able_to_start = False
            if res.user_id.id == self.env.user.id:
                res.is_able_to_start = True

    def get_access_validation(self):
        for res in self:
            res.is_access_validation = False
            if res.user_assistant_id.id == self.env.user.id:
                res.is_access_validation = True

    @api.model
    def create(self, vals):
        if vals.get('number', 'New') == 'New':
            today = fields.Date.today()
            seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(today))
            vals['number'] = self.env['ir.sequence'].next_by_code('maintenance.request.reset', sequence_date=seq_date) or 'New'
        request = super(MaintenanceRequest, self).create(vals)
        if not request.stage_id.done:
            request.closed_date = False
        elif request.stage_id.done and not request.closed_date:
            request.closed_date = fields.Datetime.today()
        return request

    def write(self, vals):
        if 'system_category_id' in vals:
            cate_id = self.env['system.category'].search([('id', '=', vals['system_category_id'])])
            if not 'name' in vals:
                vals['name'] = self.name.split('-')[0].strip() + ' - ' + cate_id.name
            else:
                vals['name'] = vals['name'] + ' - ' + cate_id.name
        res = super(MaintenanceRequest, self).write(vals)
        if 'stage_id' in vals:
            self.filtered(lambda m: m.stage_id.done).write({'closed_date': fields.Datetime.today()})
            self.filtered(lambda m: not m.stage_id.done).write({'closed_date': False})
        return res

    @api.onchange('maintenance_team_id')
    def onchange_maintenance_team_id(self):
        self.user_id = False
        if self.maintenance_team_id:
            return {'domain': {'user_id': [('id', 'in', self.maintenance_team_id.member_ids.ids)]}}

    @api.onchange('equipment_category_id')
    def onchange_equipment_category_id(self):
        if self.equipment_category_id:
            self.equipment_id = False

    @api.onchange('maintenance_team_id')
    def _get_warehouse_value(self):
        warehouse_record = self.env['stock.location'].search([('maintenance_team_id', '=', self.maintenance_team_id.id)], limit=1)
        if warehouse_record:
            self.location_id = warehouse_record.id
        else:
            self.location_id = False

    def compute_spare_parts_count(self):
        for rec in self:
            count = len(self.env['repair.order'].search([('maintenance_id', '=', self.id)]))
            rec.spare_parts_count = count

    @api.depends('state', 'user_id', 'employee_id', 'request_validation')
    def check_is_request_validation(self):
        for rec in self:
            if rec.state == 'in_progress' and self.env.user.id == rec.employee_id.user_id.id and rec.request_validation == 'supervisor':
                rec.is_request_validation = True
            elif rec.state == 'in_progress' and self.env.user.id == rec.user_id.id and rec.request_validation == 'responsible':
                rec.is_request_validation = True
            else:
                rec.is_request_validation = False

    @api.depends('stage_id')
    def _get_check_stages(self):
        for rec in self:
            if rec.stage_id.id == self.env.ref('maintenance.stage_3').id:
                rec.is_repair_stage = True
            else:
                rec.is_repair_stage = False

            if rec.stage_id.id == self.env.ref('iwesabe_helpdesk_maintenance.validation_record').id:
                rec.is_validation_stage = True
            else:
                rec.is_validation_stage = False

    @api.depends('close_date', 'stage_id', 'request_date')
    def compute_execution_day(self):
        for rec in self:
            if rec.close_date and rec.request_date and rec.stage_id.id == self.env.ref('maintenance.stage_3').id:
                request_date = datetime.strptime(str(rec.request_date), '%Y-%m-%d %H:%M:%S').date()
                close_date = datetime.strptime(str(rec.close_date), '%Y-%m-%d').date()

                diff_date = close_date-request_date
                rec.execution_day = int(diff_date.days)
            else:
                rec.execution_day = 0

    # close_date, request_date
    # @api.onchange('stage_id', 'create_date')
    @api.depends('stage_id')
    def compute_execution_time_day(self):
        for res in self:
            res.execution_time = False
            if res.create_date and res.stage_id.id == self.env.ref('maintenance.stage_3').id and not res.check_day_time:
                # res.execution_time = " "
                today_datetime = datetime.strptime(str(datetime.today()).split(".")[0], '%Y-%m-%d %H:%M:%S')
                create_date = datetime.strptime(str(res.create_date).split(".")[0], '%Y-%m-%d %H:%M:%S')
                diff_time = today_datetime - create_date
                print ("diff_time", diff_time)
                days = diff_time.days
                remain_sec = diff_time
                if days > 0:
                    remain_sec = diff_time.total_seconds() - (days * 86400)
                execution_time = str(timedelta(seconds=remain_sec))
                res.execution_time = execution_time
                res.check_day_time = True


    def send_mail_repair(self):
        template_id = self.env.ref('iwesabe_helpdesk_maintenance.send_mail_maintenance_repair')

        from_email = self.employee_id.user_id.email
        to_email = [self.employee_id.user_id.email, self.user_id.email, self.user_assistant_id.email]
        for email_to in to_email:
            template_id.write({
                'email_to': email_to,
                'email_from': from_email,
            })
            template_id.send_mail(self.id, force_send=True)

    def ask_approve_button(self):
        if self.request_validation == 'supervisor':
            template_id = self.env.ref('iwesabe_helpdesk_maintenance.send_mail_maintenance_ask_approve')
            from_email = self.env.user.email
            email_to_list = self.get_email_to()
            for user in email_to_list:
                template_id.write({
                    'email_to': user,
                    'email_from': from_email,
                })
            template_id.send_mail(self.id, force_send=True)
        self.state = 'under_validation'

    def validation_button(self):
        if self.request_validation == 'responsible':
            template_id = self.env.ref('iwesabe_helpdesk_maintenance.send_mail_maintenance_request_approve')
            from_email = self.env.user.email
            to_email = self.user_id.email
            template_id.write({
                'email_to': to_email,
                'email_from': from_email,
            })
            template_id.send_mail(self.id, force_send=True)
        self.state = 'under_validation'

    # def reject_button(self):
    #     self.state='draft'
    #     template_id = self.env.ref('iwesabe_helpdesk_maintenance.send_mail_reject_maintenance_repair')
    #     from_email = self.employee_id.user_id.email
    #     for email_to in self.maintenance_team_id.member_ids:
    #         template_id.write({
    #             'email_to': email_to.email,
    #             'email_from': from_email,
    #         })
    #         send_mails = template_id.send_mail(self.id, force_send=True)

    def submit_button(self):
        self.state = 'submit'
        template_id = self.env.ref('iwesabe_helpdesk_maintenance.send_mail_submit_maintenance_repair')
        template_id.write({'email_to': self.user_id.email})
        template_id.send_mail(self.id, force_send=True)

    def start_repair_button(self):
        self.state = 'in_progress'
        self.stage_id = self.env.ref('maintenance.stage_1').id

    def submit_set_to_new_requests(self):
        self.state = 'draft'

    def under_validation_button(self):
        if self.request_validation == 'responsible':
            template_id = self.env.ref('iwesabe_helpdesk_maintenance.send_mail_maintenance_validation')
            from_email = self.env.user.email
            to_email = self.user_id.email
            template_id.write({
                'email_to': to_email,
                'email_from': from_email,
            })
            template_id.send_mail(self.id, force_send=True)
        else:
            template_id = self.env.ref('iwesabe_helpdesk_maintenance.send_mail_maintenance_validation')
            from_email = self.env.user.email
            email_to_list = self.get_email_to()
            for user in email_to_list:
                template_id.write({
                    'email_to': user,
                    'email_from': from_email,
                })
            template_id.send_mail(self.id, force_send=True)

        self.state = 'repaired'

    @api.model
    def get_email_to(self):
        email_list = []
        stock_user_group = self.env.ref("iwesabe_helpdesk_maintenance.technical_responsible_group")
        email_list += [usr.partner_id.email for usr in stock_user_group.users if usr.partner_id.email]
        employee_email = self.employee_id.work_email
        email_list.append(employee_email)
        return email_list

    def return_repair_button(self):
        if self.request_validation == 'responsible':
            template_id = self.env.ref('iwesabe_helpdesk_maintenance.send_mail_maintenance_return_to_repair')
            from_email = self.env.user.email
            to_email = self.user_id.email
            template_id.write({
                'email_to': to_email,
                'email_from': from_email,
            })
            template_id.send_mail(self.id, force_send=True)

            wiz_id = self.env['maintenance.request.wizard'].create(
                        {'maintenance_id': self.id})
            return {
                'name': _('Return To Repair'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'maintenance.request.wizard',
                'views': [(self.env.ref('iwesabe_helpdesk_maintenance.form_view_maintenance_request_wizard').id, 'form')],
                'view_id': self.env.ref('iwesabe_helpdesk_maintenance.form_view_maintenance_request_wizard').id,
                'target': 'new',
                'res_id': wiz_id.id,
            }
        else:
            template_id = self.env.ref('iwesabe_helpdesk_maintenance.send_mail_maintenance_return_to_repair')
            from_email = self.env.user.email            
            email_to_list = self.get_email_to()
            for user in email_to_list:
                template_id.write({
                    'email_to': user,
                    'email_from': from_email,
                })
                template_id.send_mail(self.id, force_send=True)

            wiz_id = self.env['maintenance.request.wizard'].create(
                        {'maintenance_id': self.id})
            return {
                'name': _('Return To Repair'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'maintenance.request.wizard',
                'views': [(self.env.ref('iwesabe_helpdesk_maintenance.form_view_maintenance_request_wizard').id, 'form')],
                'view_id': self.env.ref('iwesabe_helpdesk_maintenance.form_view_maintenance_request_wizard').id,
                'target': 'new',
                'res_id': wiz_id.id,
            }

    def create_spare_parts(self):
        ctx = {'default_repair_eqp_id': self.equipment_id.id,'user_id': self.user_id.id,
             'default_maintenance_id': self.id,
             'default_location_id': self.company_id.internal_transit_location_id.id,
             'default_company_id': self.company_id.id,
             'default_location_property_id': self.property_id.id}
        return {
            'name': "Spare Parts",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'repair.order',
            'context': ctx,
            'view_id': self.env.ref('repair.view_repair_order_form').id,
            'target': 'current'
        }

    def maintenance_spare_records(self):
        return {
            'name': _('Spare Parts'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'repair.order',
            'domain': [('maintenance_id', '=', self.id)],
        }

    @api.onchange('equipment_category_id', 'property_type_id', 'system_category_id', 'property_id',
                  'main_zone_location_id', 'module_porperty_zone_id')
    def filter_equipment_value(self):
        lines = []
        lines_property = []

        equipment_record = self.env['maintenance.equipment'].search([])
        property_record = self.env['property.property'].search([])

        for prop in property_record:
            if (self.property_type_id.id == prop.property_type_id.id or not self.property_type_id)\
                and (self.main_zone_location_id.id == prop.main_zone_location_id.id or not self.main_zone_location_id)\
                and (self.module_porperty_zone_id.id == prop.zone_id.id or not self.module_porperty_zone_id):
                lines_property.append(prop.id)

        for equip in equipment_record:

            if (self.equipment_category_id.id == equip.category_id.id or not self.equipment_category_id)\
                    and (self.property_type_id.id == equip.property_type_id.id or not self.property_type_id)\
                    and (self.system_category_id.id == equip.system_cat_id.id or not self.system_category_id) \
                    and (self.property_id.id == equip.location_id.id or not self.property_id) \
                    and (self.main_zone_location_id.id == equip.main_zone_location_id.id or not self.main_zone_location_id)\
                    and (self.module_porperty_zone_id.id == equip.module_property_zone_id.id or not self.module_porperty_zone_id):
                lines.append(equip.id)

        return {'domain': {'property_id': [('id', 'in', lines_property)], 'equipment_id': [('id', 'in', lines)]}}

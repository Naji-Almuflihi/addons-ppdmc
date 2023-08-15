from odoo import _, api, fields, models
from odoo.exceptions import UserError


class WorkOrderRequest(models.Model):
    _name = 'work.order.request'
    _inherit = ['mail.thread']
    _rec_name = 'din'
    _description = 'Work Order Request'

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'work.order.request') or 'New'
            return super(WorkOrderRequest, self).create(vals)

    din = fields.Char(string="DIN", readonly=True, states={'draft': [('readonly', False)]})
    rn = fields.Integer(string="RN", readonly=True, states={'draft': [('readonly', False)]})
    date = fields.Date(string='Date', readonly=True, states={'draft': [('readonly', False)]})
    name = fields.Char(string='Name', default=_('New'), index=True,
                       copy=False, readonly=True)
    request_date = fields.Date(string='Request Date', readonly=True, states={'draft': [('readonly', False)]})
    request_date_hijri = fields.Date(string='Request Date (Hijri)', readonly=True)
    mode = fields.Selection([('new', 'New'), ('renewal', 'Renewal')], string="Mode", readonly=True, states={'draft': [('readonly', False)]})
    work_type = fields.Selection([('pm', 'PM'), ('cm', 'CM'), ('emergency', 'Emergency'), ('new', 'New')], string='Work Type', readonly=True, states={'draft': [('readonly', False)]})
    category = fields.Selection([('ulv', 'ULV'), ('mech', 'MECH'), ('elect', 'ELECT'), ('civil', 'CIVIL'), ('other', 'OTHER')], string='Category', readonly=True, states={'draft': [('readonly', False)]})
    other_category = fields.Char(string='Other Category', readonly=True, states={'draft': [('readonly', False)]})
    contactor_id = fields.Many2one('maintenance.team', string='Sub Contactor', readonly=True, states={'draft': [('readonly', False)]})
    zone_location_id = fields.Many2one('zone.location', string='Work Area', readonly=True, states={'draft': [('readonly', False)]})
    period = fields.Selection([('hour', 'Hour'), ('day', 'Day')], string='Period', readonly=True, states={'draft': [('readonly', False)]})
    period_day = fields.Integer(string='Day', readonly=True, states={'draft': [('readonly', False)]})
    period_hour = fields.Integer(string='Hour', readonly=True, states={'draft': [('readonly', False)]})
    employee_id = fields.Many2one('hr.employee', string='Requester', readonly=True, states={'draft': [('readonly', False)]})
    contact_no = fields.Char(related='employee_id.mobile_phone', string='Contact No.', readonly=True, states={'draft': [('readonly', False)]})
    man_power = fields.Integer(string='ManPower', readonly=True, states={'draft': [('readonly', False)]})
    start_date = fields.Date(string='Start Date', readonly=True, states={'draft': [('readonly', False)]})
    start_time = fields.Float(string='Start Time', readonly=True, states={'draft': [('readonly', False)]})
    start_am_pm = fields.Selection([('am', 'AM'), ('pm', 'PM')], string='Start AM/PM', readonly=True, states={'draft': [('readonly', False)]})
    end_date = fields.Date(string='End Date', readonly=True, states={'draft': [('readonly', False)]})
    end_time = fields.Float(string='End Time', readonly=True, states={'draft': [('readonly', False)]})
    end_am_pm = fields.Selection([('am', 'AM'), ('pm', 'PM')], string='End AM/PM', readonly=True, states={'draft': [('readonly', False)]})
    work_description = fields.Html(string='Work Description', readonly=True, states={'draft': [('readonly', False)]})
    start_date_hijri = fields.Date(string='Start Date Hijri', readonly=True, states={'draft': [('readonly', False)]})
    start_time_hijri = fields.Float(string='Start Time Hijri', readonly=True, states={'draft': [('readonly', False)]})
    start_am_pm_hijri = fields.Selection([('am', 'Am'), ('pm', 'PM')], string='Start AM/PM Hijri', readonly=True, states={'draft': [('readonly', False)]})
    end_date_hijri = fields.Date(string='End Date Hijri', readonly=True, states={'draft': [('readonly', False)]})
    end_time_hijri = fields.Float(string='End Time Hijri', readonly=True, states={'draft': [('readonly', False)]})
    end_am_pm_hijri = fields.Selection([('am', 'Am'), ('pm', 'PM')], string='End AM/PM Hijri', readonly=True, states={'draft': [('readonly', False)]})
    spare_part = fields.Selection([('required', 'Required'), ('not_required', 'Not Required')], string='Spare Part', readonly=True, states={'draft': [('readonly', False)]})
    product_ids = fields.Many2many('product.template', string='Products', readonly=True, states={'draft': [('readonly', False)]})
    affected_system_location = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Affected System/Locations', readonly=True, states={'draft': [('readonly', False)]})
    equipment_ids = fields.Many2many('tenancy.equipment', string='Equipments', readonly=True, states={'draft': [('readonly', False)]})
    system_category_ids = fields.Many2many("system.category", string="System Category", readonly=True, states={'draft': [('readonly', False)]})
    property_ids = fields.Many2many('property.property', string='Property', readonly=True, states={'draft': [('readonly', False)]})
    # equipment_id = fields.Many2one('tenancy.equipment', string='Equipment Id')
    # system_category_id = fields.Many2one('system.category', string='System Category Id')
    # property_id = fields.Many2one('property.property', string='Property Id')
    instruction_1 = fields.Text(string='Instruction 1', default='Work Request to be filled by concerned contractor’s head including (Work area, Used equipment, Number of manpower, Period and Brief work description)', readonly=True, states={'draft': [('readonly', False)]})
    instruction_2 = fields.Text(string='Instruction 2', default='Work Request to be approved by Maintenance Supervisor.', readonly=True, states={'draft': [('readonly', False)]})
    instruction_3 = fields.Text(string='Instruction 3', default='Work Request also needs to be approved by Operation Department and Safety Department and a copy to be submitted (after approval) to Maintenance Department for record, also requestor must keep copy at work place.', readonly=True, states={'draft': [('readonly', False)]})
    instruction_4 = fields.Text(string='Instruction 4', default='Work must be completed within the approved requested time. If not, a renewal Work Request to be issued', readonly=True, states={'draft': [('readonly', False)]})
    instruction_5 = fields.Text(string='Instruction 5', default='At work place, requestor must take all safety precautions as per Safety and Security regulations and make sure the work will not affect other areas.', readonly=True, states={'draft': [('readonly', False)]})
    instruction_6 = fields.Text(string='Instruction 6', default='To ensure that all equipment, tools waste & excessive materials to be removed and to leave the place in a clean condition.', readonly=True, states={'draft': [('readonly', False)]})
    instruction_7 = fields.Text(string='Instruction 7', default='In case of work requires more than a company; the coordination must be done thru Maintenance Supervisor to avoid any conflict.', readonly=True, states={'draft': [('readonly', False)]})
    instruction_8 = fields.Text(string='Instruction 8', default='Should be take  all the KAIA related Dep. approval as following: KAIA Engineering Dep. for (New Installation/Project) , KAIA Maintenance and safety Dep. ( in case of work at apron side which contain digging or using crane )', readonly=True, states={'draft': [('readonly', False)]})
    instruction_9 = fields.Text(string='Instruction 9', default='For assistance call: EXT. 8030', readonly=True, states={'draft': [('readonly', False)]})
    instruction_10 = fields.Text(string='Instruction 10', default='For emergency call: EXT. 8111', readonly=True, states={'draft': [('readonly', False)]})
    instruction_arabic_1 = fields.Text(string='Instruction Arabic 1', default='تعبئة نموذج طلب تنفيذ العمل وتوقيعه من مشرف جهة التنفيذ مع تحديد (منطقة العمل ، المعدات المستخدمة ،عدد العمال ،مدة تنفيذ العمل، وصف العمل).', readonly=True, states={'draft': [('readonly', False)]})
    instruction_arabic_2 = fields.Text(string='Instruction Arabic 2', default='اعتماد طلب تنفيذ العمل من مشرف الصيانة.', readonly=True, states={'draft': [('readonly', False)]})
    instruction_arabic_3 = fields.Text(string='Instruction Arabic 3', default='اعتماد طلب تنفيذ العمل من إدارة العمليات وإدارة السلامة وتسليم نسخة منه إلى إدارة الصيانة وحفظ نسخة في مكان العمل.', readonly=True, states={'draft': [('readonly', False)]})
    instruction_arabic_4 = fields.Text(string='Instruction Arabic 4', default='إنهاء الأعمال خلال المدة المقررة طبقا لطلب تنفيذ العمل، وفي حالة تمديد المدة يتطلب عمل تجديد لطلب التنفيذ.', readonly=True, states={'draft': [('readonly', False)]})
    instruction_arabic_5 = fields.Text(string='Instruction Arabic 5', default='اتخاذ الاحتياطات والتدابير في مكان العمل والتأكد من عدم تأثيرها على أماكن أخرى، مع الالتزام بتعليمات الأمن والسلامة.', readonly=True, states={'draft': [('readonly', False)]})
    instruction_arabic_6 = fields.Text(string='Instruction Arabic 6', default='إعادة مكان العمل إلى ما كان عليه سابقا، ورفع جميع المخلفات والمعدات والتأكد من نظافته.', readonly=True, states={'draft': [('readonly', False)]})
    instruction_arabic_7 = fields.Text(string='Instruction Arabic 7', default='في حال تنفيذ عمل يتطلب أكثر من جهة تنفيذ يجب أن يتم التنسيق مع مشرف الصيانة منعا لحدوث خلل في الأداء.', readonly=True, states={'draft': [('readonly', False)]})
    instruction_arabic_8 = fields.Text(string='Instruction Arabic 8', default='يجب اعتماد النموذج للأعمال أدناه من الادارات المعنية بمطار الملك عبد العزيز:\n• تركيبات ومشاريع جديدة – الإدارة الهندسية\n• أعمال الحفريات بساحة الطيران – إدارة الصيانة\n• استخدام الرافعة – إدارة السلامة', readonly=True, states={'draft': [('readonly', False)]})
    instruction_arabic_9 = fields.Text(string='Instruction Arabic 9', default='للمساعدة يرجى الإتصل على تحويلة :  ٨٠٣٠', readonly=True, states={'draft': [('readonly', False)]})
    instruction_arabic_10 = fields.Text(string='Instruction Arabic 10', default='للطوارئ يرجى الإتصل على تحويلة  : ٨١١١', readonly=True, states={'draft': [('readonly', False)]})
    maintenance_management_user_id = fields.Many2one('res.users', string='Maintenance Management User', readonly=True, states={'draft': [('readonly', False)]})
    safety_management_user_id = fields.Many2one('res.users', string='Safety Management User', readonly=True, states={'draft': [('readonly', False)]})
    operation_management_user_id = fields.Many2one('res.users', string='Operation Management User', readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection(
        string='State',
        selection=[
            ('draft', 'New'),
            ('confirm', 'Waiting Approval'),
            ('refuse', 'Refused'),
            ('validate1', 'Waiting Second Approval'),
            ('validate2', 'Waiting Third Approval'),
            ('approved', 'Approved'),
            ('cancel', 'Cancelled')
        ],
        default='draft'
    )
    sscl_bool = fields.Boolean(string='SSCL', readonly=True, states={'draft': [('readonly', False)]})
    btam_bool = fields.Boolean(string='BTAM', readonly=True, states={'draft': [('readonly', False)]})
    other_bool = fields.Boolean(string='Other', readonly=True, states={'draft': [('readonly', False)]})
    satco_bool = fields.Boolean(string='SATCO', readonly=True, states={'draft': [('readonly', False)]})
    abtss_bool = fields.Boolean(string='ABTSS', readonly=True, states={'draft': [('readonly', False)]})
    kone_bool = fields.Boolean(string='KONE', readonly=True, states={'draft': [('readonly', False)]})
    iblic_bool = fields.Boolean(string='IBLIC/VL', readonly=True, states={'draft': [('readonly', False)]})
    tilad_bool = fields.Boolean(string='TILAD', readonly=True, states={'draft': [('readonly', False)]})
    terminal_bool = fields.Boolean(string='Terminal', readonly=True, states={'draft': [('readonly', False)]})
    plaza_bool = fields.Boolean(string='Plaza', readonly=True, states={'draft': [('readonly', False)]})
    apron_bool = fields.Boolean(string='Apron', readonly=True, states={'draft': [('readonly', False)]})
    roof_top_bool = fields.Boolean(string='Roof Top', readonly=True, states={'draft': [('readonly', False)]})
    ra_bool = fields.Boolean(string='RA', readonly=True, states={'draft': [('readonly', False)]})
    other_work_area_bool = fields.Boolean(string='Other Work area', readonly=True, states={'draft': [('readonly', False)]})

    def action_create_maintenance_request(self):
        return {
              'res_model': 'maintenance.request',
              'type': 'ir.actions.act_window',
              'view_type': 'form',
              'view_id': self.env.ref('maintenance.hr_equipment_request_view_form').id,
              'view_mode': 'form',
              'target': 'current',
          }

    @api.onchange('contactor_id')
    def onchange_contractor(self):
        contractor = self.env['maintenance.team'].search([('id', '=', self.contactor_id.id)])
        if contractor.name == 'SSCL':
            self.sscl_bool = True
        if contractor.name == 'BT Advanced Operations & Maintenance BTAM':
            self.btam_bool = True
        if contractor.name == 'Other':
            self.other_bool = True
        if contractor.name == 'SATCO':
            self.satco_bool = True
        if contractor.name == 'ABTSS':
            self.abtss_bool = True
        if contractor.name == 'KONE':
            self.kone_bool = True
        if contractor.name == 'IBLIC / VL':
            self.iblic_bool = True
        if contractor.name == 'TILAD':
            self.tilad_bool = True

    @api.onchange('zone_location_id')
    def onchange_zone_location(self):
        zone_location = self.env['zone.location'].search([('id', '=', self.zone_location_id.id)])
        if zone_location.name == 'TERMINAL':
            self.terminal_bool = True
        if zone_location.name == 'PLAZA':
            self.plaza_bool = True
        if zone_location.name == 'APRON':
            self.apron_bool = True
        if zone_location.name == 'ROOF TOP':
            self.roof_top_bool = True
        if zone_location.name == 'REOMTE.AREA':
            self.ra_bool = True
        if zone_location.name == 'Warehouse' or 'WAREHOUSE' or 'PARKING':
            self.other_work_area_bool = True

    def action_submit(self):
        self._send_mail_to_users()
        self.write({'state': 'confirm'})

    def action_second_submit(self):
        if not self.user_has_groups('iwesabe_work_order_request.maintenance_management_group'):
            raise UserError(_("You do not have access to approve!"))
        self.maintenance_management_user_id = self.env.user.id
        self.write({'state': 'validate1'})

    def action_third_submit(self):
        if not self.user_has_groups('iwesabe_work_order_request.safety_management_group'):
            raise UserError(_("You do not have access to approve!"))
        self.safety_management_user_id = self.env.user.id
        self.write({'state': 'validate2'})

    def action_approve(self):
        if not self.user_has_groups('iwesabe_work_order_request.operation_management_group'):
            raise UserError(_("You do not have access to approve!"))
        self.operation_management_user_id = self.env.user.id
        self.write({'state': 'approved'})

    def approve_progressbar(self):
        active_user = self.env.user.id
        maintenance_user_group = self.env.ref("iwesabe_work_order_request.maintenance_management_group")
        safety_user_group = self.env.ref("iwesabe_work_order_request.safety_management_group")
        operation_user_group = self.env.ref("iwesabe_work_order_request.operation_management_group")
        if maintenance_user_group.users:
            if not self.maintenance_management_user_id:
                if len(maintenance_user_group.users) > 1:
                    for group_id in maintenance_user_group.users:
                        if group_id.id == active_user:
                            self.maintenance_management_user_id = group_id.id
                elif maintenance_user_group.users.id == active_user:
                    self.maintenance_management_user_id = active_user
                else:
                    raise UserError(_("You are not Maintenance Manager!"))
            if safety_user_group.users:
                if not self.safety_management_user_id:
                    if len(safety_user_group.users) > 1:
                        for group_id in safety_user_group.users:
                            if group_id.id == active_user:
                                self.safety_management_user_id = group_id.id
                    elif safety_user_group.users.id == active_user:
                        self.safety_management_user_id = active_user
                    else:
                        raise UserError(_("You are not Safety Manager!"))
            if operation_user_group.users:
                if not self.operation_management_user_id:
                    if len(operation_user_group.users) > 1:
                        for group_id in operation_user_group.users:
                            if group_id.id == active_user:
                                self.operation_management_user_id = group_id.id
                                self.state = 'approved'
                    elif operation_user_group.users.id == active_user:
                        self.operation_management_user_id = active_user
                        self.state = 'approved'
                    else:
                        raise UserError(_("You are not Operation Manager!"))
        else:
            raise UserError(_("Add Group in User!"))

    def _get_management_users(self):
        maintenance_user_group = self.env.ref("iwesabe_work_order_request.maintenance_management_group")
        safety_user_group = self.env.ref("iwesabe_work_order_request.safety_management_group")
        operation_user_group = self.env.ref("iwesabe_work_order_request.operation_management_group")
        return maintenance_user_group.users + safety_user_group.users + operation_user_group.users

    @api.model
    def get_email_to(self, management_users):
        email_list = []
        if management_users:
            email_list += [usr.partner_id.email for usr in management_users if usr.partner_id.email]
        return email_list

    def _send_mail_to_users(self):
        template = self.env.ref('iwesabe_work_order_request.email_group_user_reminder')
        assert template._name == 'mail.template'
        management_users = self._get_management_users()
        email_to_list = self.get_email_to(management_users)
        from_email = self.env.user.email
        for user in email_to_list:
            template_values = {'email_to': user, 'email_from': from_email}
            template.sudo().write(template_values)
            template.sudo().send_mail(self.id, force_send=True, raise_exception=True)
        self._send_user_notification(management_users)

    def _send_user_notification(self, management_users):
        if not management_users:
            return False
        refs_source = ["<a href=# data-oe-model=res.users data-oe-id=%d>@%s</a>" % (user.id, user.name) for user in management_users]
        message_source = _("Work Order has been created %s" % ', '.join(refs_source))
        self.message_post(body=message_source)

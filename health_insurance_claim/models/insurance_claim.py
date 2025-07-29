# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import json


class InsuranceClaim(models.Model):
    _name = 'hic.claim'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'his.mixin', 'clinic.qrcode.mixin']
    _description = 'Health Insurance Claim'
    _order = 'visit_date desc, id desc'
    _rec_name = 'display_name'

    # ===== BASIC INFORMATION =====
    display_name = fields.Char('Display Name', compute='_compute_display_name', store=True)
    visit_id = fields.Char(
        'Visit ID',
        required=True,
        index=True,
        help="Mã lượt khám từ HIS"
    )
    patient_id = fields.Many2one(
        'his.patient',
        string='Bệnh nhân',
        required=True,
        index=True,
        tracking=True
    )

    # ===== STATUS MANAGEMENT =====
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('validated', 'Đã xác thực'),
        ('check_in_sent', 'Đã gửi Check-in'),
        ('processing', 'Đang xử lý'),
        ('responded', 'Đã phản hồi'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
    ], string='Trạng thái', default='draft', tracking=True)

    checkin_status = fields.Selection([
        ('not_sent', 'Chưa gửi Check-in'),
        ('sent', 'Đã gửi Check-in'),
        ('failed', 'Gửi thất bại'),
    ], string='Trạng thái Check-in', default='not_sent', tracking=True)

    claim_status = fields.Selection([
        ('not_sent', 'Chưa gửi Giám định'),
        ('processing', 'Đang xử lý'),
        ('responded', 'Đã phản hồi'),
        ('sent', 'Đã gửi Giám định'),
        ('failed', 'Gửi thất bại'),
    ], string='Trạng thái Giám định', default='not_sent', tracking=True)

    # ===== PATIENT INFO (from design) =====
    patient_name = fields.Char(related='patient_id.name', string='Họ và tên', readonly=True)
    patient_dob = fields.Date(related='patient_id.birthday', string='DOB', readonly=True)
    patient_gender = fields.Selection(related='patient_id.gender', string='Giới tính', readonly=True)
    patient_citizen_id = fields.Char(related='patient_id.gov_code', string='CCCD', readonly=True)
    patient_phone = fields.Char(related='patient_id.mobile', string='SĐT', readonly=True)

    # ===== INSURANCE INFO (from design) =====
    insurance_number = fields.Char(
        related='patient_id.insurance_number',
        string='Số BHYT',
        readonly=True
    )
    insurance_benefit_code = fields.Char(
        related='patient_id.insurance_benefit_code',
        string='Mã quyền lợi',
        readonly=True
    )
    insurance_object = fields.Char(
        related='patient_id.insurance_object',
        string='Đối tượng',
        readonly=True
    )
    insurance_region_code = fields.Char(
        related='patient_id.insurance_region_code',
        string='Mã vùng',
        readonly=True
    )
    registered_hospital = fields.Char(
        related='patient_id.registered_hospital',
        string='Nơi ĐK KCB',
        readonly=True
    )
    insurance_valid_from = fields.Date(
        related='patient_id.insurance_valid_from',
        string='Từ Ngày',
        readonly=True
    )
    insurance_valid_to = fields.Date(
        related='patient_id.insurance_valid_to',
        string='Đến ngày',
        readonly=True
    )
    rare_disease_code = fields.Char(
        related='patient_id.rare_disease_code',
        string='Mã bệnh hiếm (nếu có)',
        readonly=True
    )
    five_year_continuous_date = fields.Date(
        related='patient_id.five_year_continuous_date',
        string='Ngày đủ 5 năm liên tục',
        readonly=True
    )
    copay_exemption_start = fields.Date(
        related='patient_id.copay_exemption_start',
        string='Ngày BĐ được miễn Cùng CT',
        readonly=True
    )
    copay_exemption_end = fields.Date(
        related='patient_id.copay_exemption_end',
        string='Ngày KT được miễn Cùng CT',
        readonly=True
    )
    benefit_percentage = fields.Float(
        related='patient_id.benefit_percentage',
        string='Mức hưởng BHYT',
        readonly=True
    )

    # ===== TRANSFER INFO =====
    transfer_number = fields.Char('Số chuyển tuyến')
    transfer_from = fields.Char('Nơi chuyển tuyến')
    transfer_date = fields.Date('Ngày chuyển tuyến')

    # ===== VISIT INFORMATION (from design) =====
    visit_date = fields.Datetime(
        'Đến khám ngày',
        required=True,
        default=fields.Datetime.now,
        tracking=True
    )
    admission_date = fields.Datetime('Ngày vào nội trú')
    discharge_date = fields.Datetime('Ngày ra')
    treatment_days = fields.Integer(
        'Số ngày điều trị',
        compute='_compute_treatment_days',
        store=True
    )

    # ===== MEDICAL INFORMATION =====
    admission_reason = fields.Text('Lý do vào viện')
    inpatient_reason = fields.Text('Lý do vào nội trú')
    inpatient_reason_code = fields.Char('Mã lý do vào nội trú')

    admission_diagnosis = fields.Text('Chẩn đoán vào viện')
    discharge_diagnosis = fields.Text('Chẩn đoán ra viện')

    # ICD Codes
    primary_disease_code = fields.Char(
        'Mã bệnh chính (ICD 10)',
        help="Ví dụ: E00 Bệnh tim mạch"
    )
    secondary_disease_codes = fields.Char(
        'Mã bệnh kèm theo (ICD 10)',
        help="Ví dụ: E01, E02"
    )
    traditional_medicine_code = fields.Char('Mã bệnh y học cổ truyền')
    surgery_code = fields.Char(
        'Mã PTTT Quốc tế (ICD 9 CM)',
        help="Mã phẫu thuật thủ thuật quốc tế"
    )

    # Treatment Info
    kcb_object_code = fields.Char(
        'Mã đối tượng KCB',
        default='1',
        help="1. Đúng tuyến, 2. Trái tuyến..."
    )
    accident_code = fields.Char(
        'Mã tai nạn',
        help="Mã phân loại tai nạn"
    )
    treatment_method = fields.Text('Phương pháp điều trị')
    treatment_result = fields.Char(
        'Kết quả điều trị',
        help="1. Khỏi, 2. Đỡ, 3. Không thay đổi..."
    )
    discharge_type_code = fields.Char(
        'Mã loại ra viện',
        help="1. Ra viện, 2. Chuyển viện..."
    )
    departure_place_code = fields.Char('Mã nơi đi')
    destination_place_code = fields.Char('Mã nơi đến')
    notes = fields.Text('Ghi chú')

    # ===== FINANCIAL INFORMATION (from design) =====
    settlement_year = fields.Integer(
        'Năm Quyết toán',
        default=lambda self: datetime.now().year
    )
    settlement_month = fields.Integer(
        'Tháng quyết toán',
        default=lambda self: datetime.now().month
    )
    payment_datetime = fields.Datetime(
        'Ngày thanh toán',
        default=fields.Datetime.now
    )

    # Cost breakdown
    medicine_cost = fields.Float(
        'Tiền thuốc',
        digits=(15, 0),
        help="Tổng chi phí thuốc (VND)"
    )
    medical_supply_cost = fields.Float(
        'Tiền VTYT',
        digits=(15, 0),
        help="Tổng chi phí vật tư y tế (VND)"
    )
    other_source_cost = fields.Float(
        'Nguồn khác',
        digits=(15, 0)
    )
    patient_payment = fields.Float(
        'Tiền BNTT',
        digits=(15, 0),
        help="Tiền bệnh nhân tự trả (VND)"
    )
    insurance_payment = fields.Float(
        'Tiền BHTT',
        digits=(15, 0),
        help="Tiền bảo hiểm thanh toán (VND)"
    )
    patient_copay = fields.Float(
        'Tiền BNCCT',
        digits=(15, 0),
        help="Tiền bệnh nhân cùng chi trả (VND)"
    )
    total_hospital_cost = fields.Float(
        'Tổng chi BV',
        digits=(15, 0),
        help="Tổng chi phí bệnh viện (VND)"
    )
    total_insurance_cost = fields.Float(
        'Tổng chi BH',
        digits=(15, 0),
        help="Tổng chi phí bảo hiểm (VND)"
    )
    service_insurance_payment = fields.Float(
        'Tiền BHTT GDV',
        digits=(15, 0),
        help="Tiền bảo hiểm thanh toán gói dịch vụ (VND)"
    )

    # ===== ADDITIONAL XML FIELDS =====
    hospital_code = fields.Char('Mã CSKCB', help="Mã cơ sở khám chữa bệnh")
    department_code = fields.Char('Mã khoa')
    region_code = fields.Char('Mã khu vực')
    weight = fields.Float('Cân nặng (kg)')
    child_weight = fields.Float('Cân nặng con (kg)')
    follow_up_date = fields.Date('Ngày tái khám')
    medical_record_code = fields.Char('Mã HSBA', help="Mã hồ sơ bệnh án")
    service_status_code = fields.Char('Mã TTDV', help="Mã trạng thái dịch vụ")

    # ===== RELATIONSHIPS =====
    medicine_lines = fields.One2many(
        'hic.claim.medicine',
        'claim_id',
        string='Chi tiết thuốc (XML2)'
    )
    service_lines = fields.One2many(
        'hic.claim.service',
        'claim_id',
        string='Chi tiết DVKT & VTYT (XML3)'
    )
    clinical_lines = fields.One2many(
        'hic.claim.clinical',
        'claim_id',
        string='Chi tiết dịch vụ lâm sàng (XML4)'
    )

    # ===== METADATA =====
    created_from_his = fields.Boolean(
        'Tạo từ HIS',
        default=False,
        help="Hồ sơ được tạo tự động từ HIS webhook"
    )
    his_sync_date = fields.Datetime('Ngày đồng bộ HIS')
    sent_to_bhyt_date = fields.Datetime('Ngày gửi lên BHYT')
    bhyt_response_date = fields.Datetime('Ngày phản hồi từ BHYT')
    bhyt_response_data = fields.Text('Dữ liệu phản hồi BHYT')

    # ===== COMPUTED FIELDS =====
    @api.depends('visit_id', 'patient_name')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.visit_id} - {record.patient_name or 'N/A'}"

    @api.depends('admission_date', 'discharge_date')
    def _compute_treatment_days(self):
        for record in self:
            if record.admission_date and record.discharge_date:
                delta = record.discharge_date.date() - record.admission_date.date()
                record.treatment_days = delta.days + 1
            else:
                record.treatment_days = 0

    # ===== CONSTRAINTS =====
    @api.constrains('visit_id')
    def _check_unique_visit_id(self):
        for record in self:
            if record.visit_id:
                existing = self.search([
                    ('visit_id', '=', record.visit_id),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(_("Visit ID đã tồn tại: %s") % record.visit_id)

    @api.constrains('admission_date', 'discharge_date')
    def _check_dates(self):
        for record in self:
            if record.admission_date and record.discharge_date:
                if record.discharge_date < record.admission_date:
                    raise ValidationError(_("Ngày ra viện không thể trước ngày vào viện"))

    # ===== CRUD OVERRIDES =====
    @api.model
    def create(self, vals):
        # Auto-set patient insurance info if not provided
        if 'patient_id' in vals:
            patient = self.env['his.patient'].browse(vals['patient_id'])
            if not patient.can_use_bhyt:
                raise ValidationError(_("Bệnh nhân không thể sử dụng BHYT"))

        record = super().create(vals)
        record._generate_unique_code()
        return record

    def _generate_unique_code(self):
        """Generate unique code for QR"""
        if not self.unique_code:
            self.unique_code = f"HIC{self.id:08d}"

    # ===== ACTION METHODS =====
    def action_validate(self):
        """Validate claim data before processing"""
        self.ensure_one()
        errors = []

        # Check required fields
        if not self.patient_id.insurance_number:
            errors.append("Thiếu số BHYT")
        if not self.visit_date:
            errors.append("Thiếu ngày khám")
        if not self.primary_disease_code:
            errors.append("Thiếu mã bệnh chính")

        if errors:
            raise ValidationError(_("Lỗi xác thực:\n%s") % "\n".join(errors))

        self.state = 'validated'
        self.message_post(body=_("Hồ sơ đã được xác thực"))

    def action_send_checkin(self):
        """Send check-in to BHYT gateway"""
        self.ensure_one()
        if self.state != 'validated':
            raise UserError(_("Hồ sơ phải được xác thực trước khi gửi check-in"))

        # TODO: Implement BHYT API call
        try:
            # Simulate API call
            self.checkin_status = 'sent'
            self.state = 'check_in_sent'
            self.message_post(body=_("Đã gửi check-in thành công"))
        except Exception as e:
            self.checkin_status = 'failed'
            raise UserError(_("Gửi check-in thất bại: %s") % str(e))

    def action_send_claim(self):
        """Send claim to BHYT gateway"""
        self.ensure_one()
        if self.checkin_status != 'sent':
            raise UserError(_("Phải gửi check-in thành công trước"))

        # TODO: Implement BHYT API call
        try:
            # Simulate API call
            self.claim_status = 'sent'
            self.state = 'processing'
            self.sent_to_bhyt_date = fields.Datetime.now()
            self.message_post(body=_("Đã gửi hồ sơ giám định thành công"))
        except Exception as e:
            self.claim_status = 'failed'
            raise UserError(_("Gửi hồ sơ thất bại: %s") % str(e))

    def action_sync_from_his(self):
        """Sync updated data from HIS"""
        self.ensure_one()
        # TODO: Implement HIS API call
        self.his_sync_date = fields.Datetime.now()
        self.message_post(body=_("Đã đồng bộ dữ liệu từ HIS"))

    def action_export_xml(self):
        """Export claim data to XML format"""
        self.ensure_one()
        # TODO: Implement XML generation according to 4750/QĐ-BYT
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Xuất XML'),
                'message': _('Chức năng xuất XML sẽ được triển khai'),
                'type': 'info'
            }
        }

    def action_view_xml_details(self):
        """View XML detail lines"""
        self.ensure_one()
        return {
            'name': _('Chi tiết XML'),
            'view_type': 'form',
            'res_model': 'hic.claim',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('health_insurance_claim.view_claim_xml_form').id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def action_print_claim(self):
        """Print claim report"""
        self.ensure_one()
        return self.env.ref('health_insurance_claim.action_report_claim').report_action(self)

        # ===== AUTOMATION METHODS =====

    @api.model
    def create_from_his_webhook(self, his_data):
        """Create claim from HIS webhook data"""
        patient_pid = his_data.get('patient_id')
        visit_id = his_data.get('visit_id')

        # Find patient
        patient = self.env['his.patient'].search([('patient_id', '=', patient_pid)], limit=1)
        if not patient:
            raise ValidationError(_("Không tìm thấy bệnh nhân với PID: %s") % patient_pid)

        if not patient.can_use_bhyt:
            raise ValidationError(_("Bệnh nhân không có BHYT hợp lệ"))

        # Check if claim already exists
        existing_claim = self.search([('visit_id', '=', visit_id)], limit=1)
        if existing_claim:
            return existing_claim

        # Create new claim
        vals = {
            'visit_id': visit_id,
            'patient_id': patient.id,
            'visit_date': his_data.get('visit_date', fields.Datetime.now()),
            'created_from_his': True,
            'his_sync_date': fields.Datetime.now(),
            # Map other fields from his_data
        }

        return self.create(vals)

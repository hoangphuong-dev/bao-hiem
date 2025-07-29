# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PatientExtended(models.Model):
    _inherit = 'his.patient'

    # ===== BHYT INSURANCE INFORMATION =====
    insurance_number = fields.Char(
        'Số BHYT',
        help="Số thẻ bảo hiểm y tế (DN 4 79 0126237490)"
    )
    insurance_benefit_code = fields.Char(
        'Mã quyền lợi',
        help="Mã quyền lợi BHYT (01, 02, 03...)"
    )
    insurance_object = fields.Char(
        'Đối tượng',
        help="Đối tượng BHYT (DN (80%), TE (100%)...)"
    )
    insurance_region_code = fields.Char(
        'Mã vùng',
        help="Mã vùng địa lý theo BHYT"
    )
    registered_hospital = fields.Char(
        'Nơi ĐK KCB',
        help="Nơi đăng ký khám chữa bệnh ban đầu"
    )
    insurance_valid_from = fields.Date(
        'Từ Ngày',
        help="Ngày bắt đầu hiệu lực thẻ BHYT"
    )
    insurance_valid_to = fields.Date(
        'Đến ngày',
        help="Ngày hết hiệu lực thẻ BHYT"
    )

    # ===== SPECIAL BENEFITS =====
    rare_disease_code = fields.Char(
        'Mã bệnh hiếm (nếu có)',
        help="Mã bệnh hiếm theo danh mục BHYT (D58, E10...)"
    )
    five_year_continuous_date = fields.Date(
        'Ngày đủ 5 năm liên tục',
        help="Ngày đủ điều kiện 5 năm tham gia BHYT liên tục"
    )
    copay_exemption_start = fields.Date(
        'Ngày BĐ được miễn Cùng CT',
        help="Ngày bắt đầu được miễn đồng chi trả"
    )
    copay_exemption_end = fields.Date(
        'Ngày KT được miễn Cùng CT',
        help="Ngày kết thúc được miễn đồng chi trả"
    )
    benefit_percentage = fields.Float(
        'Mức hưởng BHYT (%)',
        help="Phần trăm hưởng BHYT (80%, 100%...)",
        digits=(5, 2)
    )

    # ===== COMPUTED FIELDS =====
    insurance_status = fields.Selection([
        ('valid', 'Có hiệu lực'),
        ('expired', 'Hết hiệu lực'),
        ('not_registered', 'Chưa có BHYT'),
    ], string='Trạng thái BHYT', compute='_compute_insurance_status', store=True)

    can_use_bhyt = fields.Boolean(
        'Có thể sử dụng BHYT',
        compute='_compute_insurance_status',
        store=True
    )

    # ===== RELATIONSHIPS =====
    insurance_claims = fields.One2many(
        'hic.claim',
        'patient_id',
        string='Hồ sơ giám định BHYT'
    )
    claim_count = fields.Integer(
        'Số hồ sơ giám định',
        compute='_compute_claim_count'
    )

    # ===== COMPUTED METHODS =====
    @api.depends('insurance_number', 'insurance_valid_from', 'insurance_valid_to')
    def _compute_insurance_status(self):
        today = fields.Date.today()
        for patient in self:
            if not patient.insurance_number:
                patient.insurance_status = 'not_registered'
                patient.can_use_bhyt = False
            elif (patient.insurance_valid_from and patient.insurance_valid_from > today) or \
                (patient.insurance_valid_to and patient.insurance_valid_to < today):
                patient.insurance_status = 'expired'
                patient.can_use_bhyt = False
            else:
                patient.insurance_status = 'valid'
                patient.can_use_bhyt = True

    def _compute_claim_count(self):
        for patient in self:
            patient.claim_count = len(patient.insurance_claims)

    # ===== CONSTRAINTS =====
    @api.constrains('insurance_number')
    def _check_insurance_number_format(self):
        """Validate BHYT card number format"""
        for patient in self:
            if patient.insurance_number:
                # Basic validation for BHYT format: XX Y ZZ XXXXXXXXXX
                import re
                pattern = r'^[A-Z]{2}\s?\d{1}\s?\d{2}\s?\d{10}$'
                if not re.match(pattern, patient.insurance_number.replace(' ', '')):
                    raise ValidationError(_("Số BHYT không đúng định dạng. Ví dụ: DN 4 79 0126237490"))

    # ===== ACTIONS =====
    def action_view_insurance_claims(self):
        """Action to view patient's insurance claims"""
        self.ensure_one()
        return {
            'name': _('Hồ sơ giám định BHYT'),
            'domain': [('patient_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'hic.claim',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'context': {'default_patient_id': self.id}
        }

    def action_create_claim(self):
        """Quick action to create new insurance claim"""
        self.ensure_one()
        if not self.can_use_bhyt:
            raise ValidationError(_("Bệnh nhân không thể sử dụng BHYT. Vui lòng kiểm tra thông tin thẻ."))

        return {
            'name': _('Tạo hồ sơ giám định mới'),
            'view_type': 'form',
            'res_model': 'hic.claim',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'context': {'default_patient_id': self.id},
            'target': 'current'
        }

    def action_check_bhyt_online(self):
        """Check BHYT status online with national gateway"""
        self.ensure_one()
        if not self.insurance_number:
            raise ValidationError(_("Chưa có số BHYT để kiểm tra"))

        # TODO: Implement API call to BHYT gateway
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Kiểm tra BHYT'),
                'message': _('Chức năng kiểm tra online sẽ được triển khai'),
                'type': 'info'
            }
        }

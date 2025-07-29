# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ClaimMedicineDetail(models.Model):
    """Chi tiết thuốc (XML2)"""
    _name = 'hic.claim.medicine'
    _description = 'Claim Medicine Detail (XML2)'
    _order = 'sequence, id'

    sequence = fields.Integer('STT', default=10)
    claim_id = fields.Many2one('hic.claim', 'Hồ sơ giám định', required=True, ondelete='cascade')

    # ===== MEDICINE IDENTIFICATION =====
    medicine_code = fields.Char('Mã thuốc', required=True, help="Mã thuốc BHYT")
    his_medicine_code = fields.Char('Mã thuốc HIS', help="Mã thuốc từ HIS")
    medicine_id = fields.Many2one('hic.medicine', 'Thuốc BHYT')

    # ===== MEDICINE INFO (from XML2 spec) =====
    preparation_method_code = fields.Char('Mã Phương pháp Chế biến')
    hospital_medicine_code = fields.Char('Mã CSKCB Thuốc')
    medicine_group_code = fields.Char('Mã nhóm')
    medicine_name = fields.Char('Tên Thuốc', required=True)
    unit = fields.Char('Đơn vị tính', help="Viên, Lọ, Ml...")
    concentration = fields.Char('Hàm lượng', help="250mg, 500mg...")
    administration_route = fields.Char('Đường dùng', help="Uống, Tiêm...")
    dosage_form = fields.Char('Dạng bào chế', help="Viên nén, Dung dịch...")
    dosage = fields.Char('Liều dùng', help="1 viên x 2 lần/ngày")
    usage_instruction = fields.Char('Cách dùng', help="Sau ăn, Trước ăn...")
    registration_number = fields.Char('Số Đăng ký', help="Số đăng ký lưu hành")
    bid_info = fields.Char('Thông tin thầu')
    scope = fields.Char('Phạm vi')
    insurance_rate = fields.Float('Tỷ lệ Thanh toán Bảo hiểm (%)', digits=(5, 2))

    # ===== QUANTITY & PRICING =====
    quantity = fields.Float('Số lượng', required=True, digits=(12, 3))
    unit_price = fields.Float('Đơn giá', digits=(15, 0), help="Đơn giá (VND)")
    hospital_amount = fields.Float('Thành tiền Bệnh viện', digits=(15, 0))
    insurance_amount = fields.Float('Thành tiền bảo hiểm', digits=(15, 0))

    # ===== FUND SOURCES =====
    nsnn_other_source = fields.Float('Nguồn khác NSNN', digits=(15, 0))
    vtnn_other_source = fields.Float('Nguồn khác VTNN', digits=(15, 0))
    vttn_other_source = fields.Float('Nguồn khác VTTN', digits=(15, 0))
    remaining_other_source = fields.Float('Còn lại', digits=(15, 0))
    total_other_source = fields.Float('Tổng Nguồn khác', digits=(15, 0))
    benefit_level = fields.Float('Mức hưởng', digits=(5, 2))
    patient_self_pay = fields.Float('Bệnh nhân tự trả', digits=(15, 0))
    patient_copay = fields.Float('Bệnh nhân cùng chi trả', digits=(15, 0))
    insurance_payment = fields.Float('Bảo hiểm thanh toán', digits=(15, 0))

    # ===== SERVICE INFO =====
    department_code = fields.Char('Mã khoa')
    doctor_code = fields.Char('Mã bác sĩ')
    service_code = fields.Char('Mã Dịch vụ')
    order_date = fields.Date('Ngày y lệnh')
    execution_date = fields.Date('Ngày thực hiện y lệnh')
    surgery_code = fields.Char('Mã PTTT')
    payment_source = fields.Char('Nguồn chi trả')
    wound_recurrence = fields.Char('Vết thương tái phát')
    reserve_field = fields.Char('Dự phòng')

    # ===== COMPUTED FIELDS =====
    @api.depends('quantity', 'unit_price')
    def _compute_amounts(self):
        for line in self:
            line.hospital_amount = line.quantity * line.unit_price
            # Other amount calculations based on insurance rates


class ClaimServiceDetail(models.Model):
    """Chi tiết DVKT & VTYT (XML3)"""
    _name = 'hic.claim.service'
    _description = 'Claim Service Detail (XML3)'
    _order = 'sequence, id'

    sequence = fields.Integer('STT', default=10)
    claim_id = fields.Many2one('hic.claim', 'Hồ sơ giám định', required=True, ondelete='cascade')

    # ===== SERVICE IDENTIFICATION =====
    service_code = fields.Char('Mã dịch vụ', required=True)
    his_service_code = fields.Char('Mã dịch vụ HIS')
    service_name = fields.Char('Tên dịch vụ', required=True)
    service_type = fields.Selection([
        ('dvkt', 'DVKT'),
        ('vtyt', 'VTYT')
    ], string='Loại dịch vụ', required=True)
    service_id = fields.Many2one('hic.medical.service', 'Dịch vụ BHYT')
    supply_id = fields.Many2one('hic.medical.supply', 'VTYT BHYT')

    # ===== QUANTITY & PRICING =====
    quantity = fields.Float('Số lượng', required=True, digits=(12, 3))
    hospital_unit_price = fields.Float('Đơn giá BV', digits=(15, 0))
    insurance_unit_price = fields.Float('Đơn giá BH', digits=(15, 0))
    bid_info = fields.Char('TT thầu')
    service_payment_rate = fields.Float('Tỷ lệ TT DV (%)', digits=(5, 2))
    insurance_payment_rate = fields.Float('Tỷ lệ TT BH (%)', digits=(5, 2))
    hospital_amount = fields.Float('Thành tiền BV', digits=(15, 0))
    insurance_amount = fields.Float('Thành tiền BH', digits=(15, 0))
    direct_payment = fields.Float('T TRANTT', digits=(15, 0))
    benefit_level = fields.Float('Mức hưởng', digits=(5, 2))

    # ===== FUND SOURCES (same structure as medicine) =====
    nsnn_other_source = fields.Float('T NGUONKHAC NSNN', digits=(15, 0))
    vtnn_other_source = fields.Float('T NGUONKHAC VTNN', digits=(15, 0))
    vttn_other_source = fields.Float('T NGUONKHAC VTTN', digits=(15, 0))
    remaining_other_source = fields.Float('T NGUONKHAC CL', digits=(15, 0))
    total_other_source = fields.Float('T NGUONKHAC', digits=(15, 0))
    patient_self_pay = fields.Float('T BNTT', digits=(15, 0))
    patient_copay = fields.Float('T BNCCT', digits=(15, 0))
    insurance_payment = fields.Float('T BHTT', digits=(15, 0))

    # ===== MEDICAL INFO =====
    department_code = fields.Char('Mã khoa')
    bed_code = fields.Char('Mã giường')
    doctor_code = fields.Char('Mã bác sĩ')
    executor = fields.Char('Người thực hiện')
    disease_code = fields.Char('Mã bệnh')
    traditional_disease_code = fields.Char('Mã bệnh YHCT')
    order_date = fields.Date('Ngày y lệnh')
    execution_date = fields.Date('Ngày TH y lệnh')
    result_date = fields.Date('Ngày KQ')
    surgery_code = fields.Char('Mã PTTT')
    wound_recurrence = fields.Char('Vết thương TP')
    anesthesia_method = fields.Char('PP vô cảm')
    service_location = fields.Char('Vị trí TH DVKT')
    machine_code = fields.Char('Mã máy')
    product_model = fields.Char('Mã hiệu SP')
    reusable = fields.Char('Tái sử dụng')
    reserve_field = fields.Char('Dự phòng')


class ClaimClinicalDetail(models.Model):
    """Chi tiết dịch vụ cận lâm sàng (XML4)"""
    _name = 'hic.claim.clinical'
    _description = 'Claim Clinical Service Detail (XML4)'
    _order = 'sequence, id'

    sequence = fields.Integer('STT', default=10)
    claim_id = fields.Many2one('hic.claim', 'Hồ sơ giám định', required=True, ondelete='cascade')

    # ===== CLINICAL SERVICE INFO =====
    service_code = fields.Char('Mã dịch vụ', required=True)
    indicator_code = fields.Char('Mã chỉ số')
    indicator_name = fields.Char('Tên chỉ số')
    indicator_value = fields.Char('Giá trị')
    unit_of_measure = fields.Char('Đơn vị đo')
    description = fields.Text('Mô tả')
    conclusion = fields.Text('Kết luận')
    result_date = fields.Date('Ngày KQ')
    doctor_code = fields.Char('Mã BS đọc KQ')
    reserve_field = fields.Char('Dự phòng')


class ClaimEvolutionDetail(models.Model):
    """Chi tiết diễn biến lâm sàng (XML5)"""
    _name = 'hic.claim.evolution'
    _description = 'Claim Clinical Evolution Detail (XML5)'
    _order = 'sequence, id'

    sequence = fields.Integer('STT', default=10)
    claim_id = fields.Many2one('hic.claim', 'Hồ sơ giám định', required=True, ondelete='cascade')

    # ===== CLINICAL EVOLUTION =====
    clinical_evolution = fields.Text('Diễn biến LS', help="Diễn biến lâm sàng")
    disease_stage = fields.Char('Giai đoạn bệnh')
    consultation = fields.Text('Hội chẩn')
    surgery = fields.Text('Phẫu thuật')
    evolution_time = fields.Datetime('Thời điểm DBLS')
    executor = fields.Char('Người thực hiện')
    reserve_field = fields.Char('Dự phòng')

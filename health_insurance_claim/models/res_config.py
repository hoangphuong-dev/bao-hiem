# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # ===== BHYT GATEWAY SETTINGS =====
    bhyt_gateway_url = fields.Char(
        'BHYT Gateway URL',
        config_parameter='hic.bhyt_gateway_url',
        help="URL của cổng giám định BHYT quốc gia"
    )
    bhyt_username = fields.Char(
        'BHYT Username',
        config_parameter='hic.bhyt_username',
        help="Tên đăng nhập cổng BHYT"
    )
    bhyt_password = fields.Char(
        'BHYT Password',
        config_parameter='hic.bhyt_password',
        help="Mật khẩu cổng BHYT"
    )
    bhyt_facility_code = fields.Char(
        'Facility Code',
        config_parameter='hic.bhyt_facility_code',
        help="Mã cơ sở khám chữa bệnh"
    )

    # ===== HIS INTEGRATION SETTINGS =====
    his_api_url = fields.Char(
        'HIS API URL',
        config_parameter='hic.his_api_url',
        help="URL API của hệ thống HIS"
    )
    his_api_key = fields.Char(
        'HIS API Key',
        config_parameter='hic.his_api_key',
        help="API Key để kết nối HIS"
    )
    his_webhook_token = fields.Char(
        'HIS Webhook Token',
        config_parameter='hic.his_webhook_token',
        help="Token xác thực webhook từ HIS"
    )

    # ===== AUTO SYNC SETTINGS =====
    auto_sync_enabled = fields.Boolean(
        'Tự động đồng bộ HIS',
        config_parameter='hic.auto_sync_enabled',
        default=True,
        help="Tự động đồng bộ dữ liệu từ HIS theo lịch"
    )
    sync_interval_hours = fields.Integer(
        'Chu kỳ đồng bộ (giờ)',
        config_parameter='hic.sync_interval_hours',
        default=24,
        help="Chu kỳ đồng bộ dữ liệu từ HIS (giờ)"
    )

    # ===== VALIDATION SETTINGS =====
    require_insurance_validation = fields.Boolean(
        'Bắt buộc kiểm tra BHYT online',
        config_parameter='hic.require_insurance_validation',
        default=False,
        help="Bắt buộc kiểm tra tình trạng BHYT trực tuyến"
    )
    auto_create_claim_on_admission = fields.Boolean(
        'Tự động tạo hồ sơ khi nhập viện',
        config_parameter='hic.auto_create_claim_on_admission',
        default=True,
        help="Tự động tạo hồ sơ giám định khi bệnh nhân nhập viện"
    )

    # ===== NOTIFICATION SETTINGS =====
    notification_email = fields.Char(
        'Email thông báo',
        config_parameter='hic.notification_email',
        help="Email nhận thông báo lỗi hệ thống"
    )
    send_claim_notifications = fields.Boolean(
        'Gửi thông báo hồ sơ',
        config_parameter='hic.send_claim_notifications',
        default=True,
        help="Gửi email thông báo khi hồ sơ thay đổi trạng thái"
    )

    # ===== HIS INTEGRATION =====
    hic_his_api_url = fields.Char(
        'HIS API URL',
        config_parameter='hic.his_api_url',
        help="URL của HIS API để đồng bộ dữ liệu"
    )
    hic_his_api_token = fields.Char(
        'HIS API Token',
        config_parameter='hic.his_api_token',
        help="Token xác thực cho HIS API"
    )
    hic_auto_sync_enabled = fields.Boolean(
        'Tự động đồng bộ từ HIS',
        config_parameter='hic.auto_sync_enabled',
        default=True,
        help="Tự động tạo hồ sơ giám định khi nhận webhook từ HIS"
    )

    # ===== BHYT GATEWAY =====
    hic_bhyt_gateway_url = fields.Char(
        'BHYT Gateway URL',
        config_parameter='hic.bhyt_gateway_url',
        help="URL của cổng BHYT quốc gia"
    )
    hic_bhyt_username = fields.Char(
        'BHYT Username',
        config_parameter='hic.bhyt_username',
        help="Tài khoản đăng nhập cổng BHYT"
    )
    hic_bhyt_password = fields.Char(
        'BHYT Password',
        config_parameter='hic.bhyt_password',
        help="Mật khẩu đăng nhập cổng BHYT"
    )

    # ===== HOSPITAL INFO =====
    hic_hospital_code = fields.Char(
        'Mã bệnh viện',
        config_parameter='hic.hospital_code',
        required=True,
        help="Mã bệnh viện theo BHYT"
    )
    hic_hospital_name = fields.Char(
        'Tên bệnh viện',
        config_parameter='hic.hospital_name',
        required=True,
        help="Tên bệnh viện"
    )
    hic_hospital_level = fields.Selection([
        ('1', 'Tuyến trung ương'),
        ('2', 'Tuyến tỉnh'),
        ('3', 'Tuyến huyện'),
        ('4', 'Tuyến xã'),
    ], string='Tuyến bệnh viện',
        config_parameter='hic.hospital_level',
        help="Tuyến của bệnh viện theo phân loại BHYT")

    # ===== SYSTEM SETTINGS =====
    hic_auto_checkin = fields.Boolean(
        'Tự động gửi Check-in',
        config_parameter='hic.auto_checkin',
        default=False,
        help="Tự động gửi Check-in khi tạo hồ sơ từ HIS"
    )
    hic_api_timeout = fields.Integer(
        'API Timeout (giây)',
        config_parameter='hic.api_timeout',
        default=30,
        help="Thời gian chờ tối đa cho API calls"
    )

    def action_test_bhyt_connection(self):
        """Test connection to BHYT gateway"""
        if not self.bhyt_gateway_url:
            raise ValidationError(_("Chưa cấu hình URL BHYT Gateway"))

        # TODO: Implement actual connection test
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Test Connection'),
                'message': _('Chức năng test kết nối sẽ được triển khai'),
                'type': 'info'
            }
        }

    def action_test_his_connection(self):
        """Test connection to HIS system"""
        if not self.his_api_url:
            raise ValidationError(_("Chưa cấu hình URL HIS API"))

        # TODO: Implement actual connection test
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Test Connection'),
                'message': _('Chức năng test kết nối HIS sẽ được triển khai'),
                'type': 'info'
            }
        }

    def action_sync_his_now(self):
        """Manual sync from HIS"""
        try:
            self.env['hic.his.data'].sync_from_his()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sync Completed'),
                    'message': _('Đã đồng bộ dữ liệu từ HIS thành công'),
                    'type': 'success'
                }
            }
        except Exception as e:
            raise ValidationError(_("Lỗi đồng bộ HIS: %s") % str(e))


class Company(models.Model):
    _inherit = 'res.company'

    # ===== BHYT FACILITY INFO =====
    bhyt_facility_code = fields.Char('Mã CSKCB', help="Mã cơ sở khám chữa bệnh theo BHYT")
    bhyt_facility_name = fields.Char('Tên CSKCB', help="Tên cơ sở khám chữa bệnh")
    bhyt_facility_level = fields.Selection([
        ('1', 'Tuyến Xã'),
        ('2', 'Tuyến Huyện'),
        ('3', 'Tuyến Tỉnh'),
        ('4', 'Tuyến Trung ương'),
    ], string='Tuyến BHYT')
    bhyt_facility_type = fields.Selection([
        ('public', 'Công lập'),
        ('private', 'Tư nhân'),
    ], string='Loại hình CSKCB')

# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import base64
import xlrd
from io import BytesIO


class HICMedicine(models.Model):
    """Danh mục thuốc BHYT"""
    _name = 'hic.medicine'
    _description = 'BHYT Medicine Master Data'
    _order = 'bhyt_code'
    _rec_name = 'display_name'

    display_name = fields.Char('Display Name', compute='_compute_display_name', store=True)
    bhyt_code = fields.Char('Mã BHYT', required=True, index=True)
    bhyt_name = fields.Char('Tên thuốc BHYT', required=True)
    unit = fields.Char('Đơn vị tính', help="Viên, Lọ, Ml...")
    concentration = fields.Char('Hàm lượng', help="250mg, 500mg...")
    dosage_form = fields.Char('Dạng bào chế', help="Viên nén, Dung dịch...")
    bhyt_price = fields.Float('Đơn giá BH', digits=(15, 0))
    insurance_rate = fields.Float('Tỷ lệ TT BH (%)', digits=(5, 2))
    effective_from = fields.Date('Từ ngày')
    effective_to = fields.Date('Đến ngày')

    # ===== RELATIONSHIPS =====
    his_mappings = fields.One2many('hic.medicine.mapping', 'medicine_id', 'HIS Mappings')
    mapping_count = fields.Integer('Số lượng mapping', compute='_compute_mapping_count')

    active = fields.Boolean('Active', default=True)
    notes = fields.Text('Ghi chú')

    @api.depends('bhyt_code', 'bhyt_name')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"[{record.bhyt_code}] {record.bhyt_name}"

    def _compute_mapping_count(self):
        for record in self:
            record.mapping_count = len(record.his_mappings)

    def action_view_mappings(self):
        pass

    def action_auto_mapping(self):
        pass

    @api.constrains('bhyt_code')
    def _check_unique_code(self):
        for record in self:
            if record.bhyt_code:
                existing = self.search([
                    ('bhyt_code', '=', record.bhyt_code),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(_("Mã BHYT đã tồn tại: %s") % record.bhyt_code)


class HICMedicalService(models.Model):
    """Danh mục dịch vụ kỹ thuật BHYT"""
    _name = 'hic.medical.service'
    _description = 'BHYT Medical Service Master Data'
    _order = 'bhyt_code'
    _rec_name = 'display_name'

    display_name = fields.Char('Display Name', compute='_compute_display_name', store=True)
    bhyt_code = fields.Char('Mã BHYT', required=True, index=True)
    bhyt_name = fields.Char('Tên DVKT', required=True)
    bhyt_price = fields.Float('Đơn giá BH', digits=(15, 0))
    insurance_rate = fields.Float('Tỷ lệ TT BH (%)', digits=(5, 2))
    cost_group_code = fields.Char('Mã nhóm theo chi phí')
    effective_from = fields.Date('Từ ngày')
    effective_to = fields.Date('Đến ngày')

    # ===== RELATIONSHIPS =====
    his_mappings = fields.One2many('hic.service.mapping', 'service_id', 'HIS Mappings')
    mapping_count = fields.Integer('Số lượng mapping', compute='_compute_mapping_count')

    active = fields.Boolean('Active', default=True)
    notes = fields.Text('Ghi chú')

    @api.depends('bhyt_code', 'bhyt_name')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"[{record.bhyt_code}] {record.bhyt_name}"

    def _compute_mapping_count(self):
        for record in self:
            record.mapping_count = len(record.his_mappings)

    def action_view_mappings(self):
        pass


class HICMedicalSupply(models.Model):
    """Danh mục vật tư y tế BHYT"""
    _name = 'hic.medical.supply'
    _description = 'BHYT Medical Supply Master Data'
    _order = 'bhyt_code'
    _rec_name = 'display_name'

    display_name = fields.Char('Display Name', compute='_compute_display_name', store=True)
    bhyt_code = fields.Char('Mã BHYT', required=True, index=True)
    bhyt_name = fields.Char('Tên VTYT', required=True)
    unit = fields.Char('Đơn vị tính')
    bhyt_price = fields.Float('Đơn giá BH', digits=(15, 0))
    insurance_rate = fields.Float('Tỷ lệ TT BH (%)', digits=(5, 2))
    effective_from = fields.Date('Từ ngày')
    effective_to = fields.Date('Đến ngày')

    # ===== RELATIONSHIPS =====
    his_mappings = fields.One2many('hic.supply.mapping', 'supply_id', 'HIS Mappings')
    mapping_count = fields.Integer('Số lượng mapping', compute='_compute_mapping_count')

    active = fields.Boolean('Active', default=True)
    notes = fields.Text('Ghi chú')

    @api.depends('bhyt_code', 'bhyt_name')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"[{record.bhyt_code}] {record.bhyt_name}"

    def _compute_mapping_count(self):
        for record in self:
            record.mapping_count = len(record.his_mappings)

    def action_view_mappings(self):
        pass


class HICDepartment(models.Model):
    """Danh mục khoa phòng BHYT"""
    _name = 'hic.department'
    _description = 'BHYT Department Master Data'
    _order = 'bhyt_code'
    _rec_name = 'display_name'

    display_name = fields.Char('Display Name', compute='_compute_display_name', store=True)
    bhyt_code = fields.Char('Mã BHYT', required=True, index=True)
    bhyt_name = fields.Char('Tên khoa phòng', required=True)
    department_type = fields.Selection([
        ('inpatient', 'Nội trú'),
        ('outpatient', 'Ngoại trú'),
        ('emergency', 'Cấp cứu'),
        ('surgery', 'Phẫu thuật'),
        ('paraclinical', 'Cận lâm sàng'),
    ], string='Loại khoa phòng')

    # ===== RELATIONSHIPS =====
    his_mappings = fields.One2many('hic.department.mapping', 'department_id', 'HIS Mappings')
    mapping_count = fields.Integer('Số lượng mapping', compute='_compute_mapping_count')

    active = fields.Boolean('Active', default=True)
    notes = fields.Text('Ghi chú')

    @api.depends('bhyt_code', 'bhyt_name')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"[{record.bhyt_code}] {record.bhyt_name}"

    def _compute_mapping_count(self):
        for record in self:
            record.mapping_count = len(record.his_mappings)

    def action_view_mappings(self):
        pass


class HICExcelImport(models.TransientModel):
    """Wizard for importing Excel files"""
    _name = 'hic.excel.import'
    _description = 'Excel Import Wizard'

    data_type = fields.Selection([
        ('medicine', 'Thuốc'),
        ('service', 'DVKT'),
        ('supply', 'VTYT'),
        ('department', 'Khoa phòng'),
    ], string='Loại dữ liệu', required=True)

    excel_file = fields.Binary('File Excel', required=True)
    filename = fields.Char('Tên file')

    def action_import(self):
        """Import data from Excel file"""
        self.ensure_one()
        if not self.excel_file:
            raise ValidationError(_("Vui lòng chọn file Excel"))

        try:
            # Decode file
            file_data = base64.b64decode(self.excel_file)
            workbook = xlrd.open_workbook(file_contents=file_data)
            sheet = workbook.sheet_by_index(0)

            # Import based on data type
            if self.data_type == 'medicine':
                self._import_medicine(sheet)
            elif self.data_type == 'service':
                self._import_service(sheet)
            elif self.data_type == 'supply':
                self._import_supply(sheet)
            elif self.data_type == 'department':
                self._import_department(sheet)

        except Exception as e:
            raise ValidationError(_("Lỗi import file: %s") % str(e))

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Import thành công'),
                'message': _('Đã import dữ liệu từ file Excel'),
                'type': 'success'
            }
        }

    def _import_medicine(self, sheet):
        """Import medicine data from Excel"""
        Medicine = self.env['hic.medicine']

        # Expected columns: MA_TUONG_DUONG, TEN_DVKT_PHEDUYET, DON_GIA, Từ ngày, Đến ngày, MA_DVKT_HIS
        for row_idx in range(1, sheet.nrows):  # Skip header
            row = sheet.row_values(row_idx)
            if len(row) >= 6:
                vals = {
                    'bhyt_code': str(row[0]).strip(),
                    'bhyt_name': str(row[1]).strip(),
                    'bhyt_price': float(row[2]) if row[2] else 0,
                    'effective_from': self._excel_date_to_python(row[3]) if row[3] else False,
                    'effective_to': self._excel_date_to_python(row[4]) if row[4] else False,
                }

                # Check if exists
                existing = Medicine.search([('bhyt_code', '=', vals['bhyt_code'])])
                if existing:
                    existing.write(vals)
                else:
                    Medicine.create(vals)

    def _excel_date_to_python(self, excel_date):
        """Convert Excel date to Python date"""
        if isinstance(excel_date, float):
            return xlrd.xldate_as_datetime(excel_date, 0).date()
        return False

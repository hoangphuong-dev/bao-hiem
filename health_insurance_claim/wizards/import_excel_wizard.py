# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import base64
import xlrd
from io import BytesIO


class ImportExcelWizard(models.TransientModel):
    _name = 'hic.import.excel.wizard'
    _description = 'Import Excel Wizard'

    data_type = fields.Selection([
        ('medicine', 'Thuốc'),
        ('service', 'DVKT'),
        ('supply', 'VTYT'),
        ('department', 'Khoa phòng'),
    ], string='Loại dữ liệu', required=True)
    
    excel_file = fields.Binary('File Excel', required=True)
    filename = fields.Char('Tên file')
    
    update_existing = fields.Boolean(
        'Cập nhật dữ liệu có sẵn',
        default=True,
        help="Cập nhật nếu mã BHYT đã tồn tại"
    )
    
    # Preview fields
    preview_data = fields.Text('Preview Data', readonly=True)
    show_preview = fields.Boolean('Show Preview', default=False)

    def action_preview(self):
        """Preview Excel data before import"""
        self.ensure_one()
        if not self.excel_file:
            raise ValidationError(_("Vui lòng chọn file Excel"))
        
        try:
            # Decode and read Excel file
            file_data = base64.b64decode(self.excel_file)
            workbook = xlrd.open_workbook(file_contents=file_data)
            sheet = workbook.sheet_by_index(0)
            
            # Get first 5 rows for preview
            preview_rows = []
            for row_idx in range(min(6, sheet.nrows)):
                row_data = sheet.row_values(row_idx)
                preview_rows.append(row_data)
            
            self.preview_data = str(preview_rows)
            self.show_preview = True
            
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'hic.import.excel.wizard',
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'new',
            }
            
        except Exception as e:
            raise ValidationError(_("Lỗi đọc file Excel: %s") % str(e))

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
                imported_count = self._import_medicine(sheet)
            elif self.data_type == 'service':
                imported_count = self._import_service(sheet)
            elif self.data_type == 'supply':
                imported_count = self._import_supply(sheet)
            elif self.data_type == 'department':
                imported_count = self._import_department(sheet)
            else:
                raise ValidationError(_("Loại dữ liệu không hợp lệ"))
                
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Import thành công'),
                    'message': _('Đã import %s mục dữ liệu') % imported_count,
                    'type': 'success'
                }
            }
                
        except Exception as e:
            raise ValidationError(_("Lỗi import file: %s") % str(e))
    
    def _import_medicine(self, sheet):
        """Import medicine data from Excel"""
        Medicine = self.env['hic.medicine']
        imported_count = 0
        
        # Expected columns: MA_TUONG_DUONG, TEN_DVKT_PHEDUYET, DON_GIA, Từ ngày, Đến ngày
        for row_idx in range(1, sheet.nrows):  # Skip header
            row = sheet.row_values(row_idx)
            if len(row) >= 3 and row[0]:  # At least code and name
                vals = {
                    'bhyt_code': str(row[0]).strip(),
                    'bhyt_name': str(row[1]).strip() if row[1] else '',
                    'bhyt_price': float(row[2]) if len(row) > 2 and row[2] else 0,
                    'unit': str(row[3]).strip() if len(row) > 3 and row[3] else '',
                    'concentration': str(row[4]).strip() if len(row) > 4 and row[4] else '',
                    'effective_from': self._excel_date_to_python(row[5]) if len(row) > 5 and row[5] else False,
                    'effective_to': self._excel_date_to_python(row[6]) if len(row) > 6 and row[6] else False,
                }
                
                # Check if exists
                existing = Medicine.search([('bhyt_code', '=', vals['bhyt_code'])])
                if existing and self.update_existing:
                    existing.write(vals)
                elif not existing:
                    Medicine.create(vals)
                    imported_count += 1
        
        return imported_count
    
    def _import_service(self, sheet):
        """Import service data from Excel"""
        Service = self.env['hic.medical.service']
        imported_count = 0
        
        for row_idx in range(1, sheet.nrows):
            row = sheet.row_values(row_idx)
            if len(row) >= 3 and row[0]:
                vals = {
                    'bhyt_code': str(row[0]).strip(),
                    'bhyt_name': str(row[1]).strip() if row[1] else '',
                    'bhyt_price': float(row[2]) if len(row) > 2 and row[2] else 0,
                    'insurance_rate': float(row[3]) if len(row) > 3 and row[3] else 0,
                    'cost_group_code': str(row[4]).strip() if len(row) > 4 and row[4] else '',
                    'effective_from': self._excel_date_to_python(row[5]) if len(row) > 5 and row[5] else False,
                    'effective_to': self._excel_date_to_python(row[6]) if len(row) > 6 and row[6] else False,
                }
                
                existing = Service.search([('bhyt_code', '=', vals['bhyt_code'])])
                if existing and self.update_existing:
                    existing.write(vals)
                elif not existing:
                    Service.create(vals)
                    imported_count += 1
        
        return imported_count
    
    def _import_supply(self, sheet):
        """Import supply data from Excel"""
        Supply = self.env['hic.medical.supply']
        imported_count = 0
        
        for row_idx in range(1, sheet.nrows):
            row = sheet.row_values(row_idx)
            if len(row) >= 3 and row[0]:
                vals = {
                    'bhyt_code': str(row[0]).strip(),
                    'bhyt_name': str(row[1]).strip() if row[1] else '',
                    'bhyt_price': float(row[2]) if len(row) > 2 and row[2] else 0,
                    'unit': str(row[3]).strip() if len(row) > 3 and row[3] else '',
                    'insurance_rate': float(row[4]) if len(row) > 4 and row[4] else 0,
                    'effective_from': self._excel_date_to_python(row[5]) if len(row) > 5 and row[5] else False,
                    'effective_to': self._excel_date_to_python(row[6]) if len(row) > 6 and row[6] else False,
                }
                
                existing = Supply.search([('bhyt_code', '=', vals['bhyt_code'])])
                if existing and self.update_existing:
                    existing.write(vals)
                elif not existing:
                    Supply.create(vals)
                    imported_count += 1
        
        return imported_count
    
    def _import_department(self, sheet):
        """Import department data from Excel"""
        Department = self.env['hic.department']
        imported_count = 0
        
        for row_idx in range(1, sheet.nrows):
            row = sheet.row_values(row_idx)
            if len(row) >= 2 and row[0]:
                vals = {
                    'bhyt_code': str(row[0]).strip(),
                    'bhyt_name': str(row[1]).strip() if row[1] else '',
                    'department_type': str(row[2]).strip() if len(row) > 2 and row[2] else '',
                }
                
                existing = Department.search([('bhyt_code', '=', vals['bhyt_code'])])
                if existing and self.update_existing:
                    existing.write(vals)
                elif not existing:
                    Department.create(vals)
                    imported_count += 1
        
        return imported_count
    
    def _excel_date_to_python(self, excel_date):
        """Convert Excel date to Python date"""
        if isinstance(excel_date, float):
            try:
                return xlrd.xldate_as_datetime(excel_date, 0).date()
            except:
                return False
        return False
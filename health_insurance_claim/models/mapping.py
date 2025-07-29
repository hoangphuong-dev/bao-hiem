# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MedicineMapping(models.Model):
    """Mapping between BHYT Medicine and HIS Medicine"""
    _name = 'hic.medicine.mapping'
    _description = 'Medicine BHYT-HIS Mapping'
    _rec_name = 'display_name'

    display_name = fields.Char('Display Name', compute='_compute_display_name', store=True)
    medicine_id = fields.Many2one('hic.medicine', 'BHYT Medicine', required=True, ondelete='cascade')
    his_data_id = fields.Many2one(
        'hic.his.data',
        'HIS Medicine',
        required=True,
        domain=[('data_type', '=', 'medicine')],
        ondelete='cascade'
    )
    mapping_ratio = fields.Float('Mapping Ratio', default=1.0, help="Tỷ lệ quy đổi HIS -> BHYT")
    notes = fields.Text('Mapping Notes')
    active = fields.Boolean('Active', default=True)

    # ===== RELATED FIELDS FOR DISPLAY =====
    bhyt_code = fields.Char(related='medicine_id.bhyt_code', string='Mã BHYT', readonly=True)
    bhyt_name = fields.Char(related='medicine_id.bhyt_name', string='Tên BHYT', readonly=True)
    his_code = fields.Char(related='his_data_id.his_code', string='Mã HIS', readonly=True)
    his_name = fields.Char(related='his_data_id.his_name', string='Tên HIS', readonly=True)

    @api.depends('medicine_id', 'his_data_id')
    def _compute_display_name(self):
        for record in self:
            bhyt_name = record.medicine_id.display_name if record.medicine_id else 'N/A'
            his_name = record.his_data_id.his_name if record.his_data_id else 'N/A'
            record.display_name = f"{bhyt_name} ↔ {his_name}"

    @api.constrains('medicine_id', 'his_data_id')
    def _check_unique_mapping(self):
        """Ensure one HIS item maps to only one BHYT item"""
        for record in self:
            existing = self.search([
                ('his_data_id', '=', record.his_data_id.id),
                ('id', '!=', record.id)
            ])
            if existing:
                raise ValidationError(_("HIS Medicine đã được mapping: %s") % record.his_data_id.his_name)


class ServiceMapping(models.Model):
    """Mapping between BHYT Service and HIS Service"""
    _name = 'hic.service.mapping'
    _description = 'Service BHYT-HIS Mapping'
    _rec_name = 'display_name'

    display_name = fields.Char('Display Name', compute='_compute_display_name', store=True)
    service_id = fields.Many2one('hic.medical.service', 'BHYT Service', required=True, ondelete='cascade')
    his_data_id = fields.Many2one(
        'hic.his.data',
        'HIS Service',
        required=True,
        domain=[('data_type', '=', 'service')],
        ondelete='cascade'
    )
    mapping_ratio = fields.Float('Mapping Ratio', default=1.0)
    notes = fields.Text('Mapping Notes')
    active = fields.Boolean('Active', default=True)

    # ===== RELATED FIELDS =====
    bhyt_code = fields.Char(related='service_id.bhyt_code', string='Mã BHYT', readonly=True)
    bhyt_name = fields.Char(related='service_id.bhyt_name', string='Tên BHYT', readonly=True)
    his_code = fields.Char(related='his_data_id.his_code', string='Mã HIS', readonly=True)
    his_name = fields.Char(related='his_data_id.his_name', string='Tên HIS', readonly=True)

    @api.depends('service_id', 'his_data_id')
    def _compute_display_name(self):
        for record in self:
            bhyt_name = record.service_id.display_name if record.service_id else 'N/A'
            his_name = record.his_data_id.his_name if record.his_data_id else 'N/A'
            record.display_name = f"{bhyt_name} ↔ {his_name}"


class SupplyMapping(models.Model):
    """Mapping between BHYT Supply and HIS Supply"""
    _name = 'hic.supply.mapping'
    _description = 'Supply BHYT-HIS Mapping'
    _rec_name = 'display_name'

    display_name = fields.Char('Display Name', compute='_compute_display_name', store=True)
    supply_id = fields.Many2one('hic.medical.supply', 'BHYT Supply', required=True, ondelete='cascade')
    his_data_id = fields.Many2one(
        'hic.his.data',
        'HIS Supply',
        required=True,
        domain=[('data_type', '=', 'supply')],
        ondelete='cascade'
    )
    mapping_ratio = fields.Float('Mapping Ratio', default=1.0)
    notes = fields.Text('Mapping Notes')
    active = fields.Boolean('Active', default=True)

    # ===== RELATED FIELDS =====
    bhyt_code = fields.Char(related='supply_id.bhyt_code', string='Mã BHYT', readonly=True)
    bhyt_name = fields.Char(related='supply_id.bhyt_name', string='Tên BHYT', readonly=True)
    his_code = fields.Char(related='his_data_id.his_code', string='Mã HIS', readonly=True)
    his_name = fields.Char(related='his_data_id.his_name', string='Tên HIS', readonly=True)

    @api.depends('supply_id', 'his_data_id')
    def _compute_display_name(self):
        for record in self:
            bhyt_name = record.supply_id.display_name if record.supply_id else 'N/A'
            his_name = record.his_data_id.his_name if record.his_data_id else 'N/A'
            record.display_name = f"{bhyt_name} ↔ {his_name}"


class DepartmentMapping(models.Model):
    """Mapping between BHYT Department and HIS Department"""
    _name = 'hic.department.mapping'
    _description = 'Department BHYT-HIS Mapping'
    _rec_name = 'display_name'

    display_name = fields.Char('Display Name', compute='_compute_display_name', store=True)
    department_id = fields.Many2one('hic.department', 'BHYT Department', required=True, ondelete='cascade')
    his_data_id = fields.Many2one(
        'hic.his.data',
        'HIS Department',
        required=True,
        domain=[('data_type', '=', 'department')],
        ondelete='cascade'
    )
    # Also map to HIS hr.department if needed
    his_department_id = fields.Many2one('hr.department', 'HIS HR Department')
    notes = fields.Text('Mapping Notes')
    active = fields.Boolean('Active', default=True)

    # ===== RELATED FIELDS =====
    bhyt_code = fields.Char(related='department_id.bhyt_code', string='Mã BHYT', readonly=True)
    bhyt_name = fields.Char(related='department_id.bhyt_name', string='Tên BHYT', readonly=True)
    his_code = fields.Char(related='his_data_id.his_code', string='Mã HIS', readonly=True)
    his_name = fields.Char(related='his_data_id.his_name', string='Tên HIS', readonly=True)

    @api.depends('department_id', 'his_data_id')
    def _compute_display_name(self):
        for record in self:
            bhyt_name = record.department_id.display_name if record.department_id else 'N/A'
            his_name = record.his_data_id.his_name if record.his_data_id else 'N/A'
            record.display_name = f"{bhyt_name} ↔ {his_name}"


class MappingWizard(models.TransientModel):
    """Wizard for bulk mapping operations"""
    _name = 'hic.mapping.wizard'
    _description = 'Mapping Wizard'

    mapping_type = fields.Selection([
        ('medicine', 'Thuốc'),
        ('service', 'DVKT'),
        ('supply', 'VTYT'),
        ('department', 'Khoa phòng'),
    ], string='Loại mapping', required=True)

    auto_mapping = fields.Boolean('Tự động mapping', default=True, help="Mapping tự động dựa trên tên")
    similarity_threshold = fields.Float('Ngưỡng tương đồng (%)', default=80.0,
                                        help="Ngưỡng tương đồng tên để auto mapping")

    def action_auto_mapping(self):
        """Perform automatic mapping based on name similarity"""
        self.ensure_one()

        if not self.auto_mapping:
            raise ValidationError(_("Vui lòng bật tự động mapping"))

        # Get unmapped HIS data
        his_data = self.env['hic.his.data'].search([
            ('data_type', '=', self.mapping_type),
            ('is_mapped', '=', False)
        ])

        # Get BHYT data
        if self.mapping_type == 'medicine':
            bhyt_model = 'hic.medicine'
            mapping_model = 'hic.medicine.mapping'
            bhyt_field = 'medicine_id'
        elif self.mapping_type == 'service':
            bhyt_model = 'hic.medical.service'
            mapping_model = 'hic.service.mapping'
            bhyt_field = 'service_id'
        elif self.mapping_type == 'supply':
            bhyt_model = 'hic.medical.supply'
            mapping_model = 'hic.supply.mapping'
            bhyt_field = 'supply_id'
        else:  # department
            bhyt_model = 'hic.department'
            mapping_model = 'hic.department.mapping'
            bhyt_field = 'department_id'

        bhyt_records = self.env[bhyt_model].search([])
        mapped_count = 0

        for his_record in his_data:
            best_match = None
            best_similarity = 0

            for bhyt_record in bhyt_records:
                similarity = self._calculate_similarity(his_record.his_name, bhyt_record.bhyt_name)
                if similarity > best_similarity and similarity >= self.similarity_threshold:
                    best_similarity = similarity
                    best_match = bhyt_record

            if best_match:
                # Create mapping
                self.env[mapping_model].create({
                    bhyt_field: best_match.id,
                    'his_data_id': his_record.id,
                    'notes': f'Auto mapped with {best_similarity:.1f}% similarity'
                })
                mapped_count += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Auto Mapping Completed'),
                'message': _('Đã mapping tự động %d mục') % mapped_count,
                'type': 'success'
            }
        }

    def _calculate_similarity(self, str1, str2):
        """Calculate similarity percentage between two strings"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio() * 100

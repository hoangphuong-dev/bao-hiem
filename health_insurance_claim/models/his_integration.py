# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import requests
import json
from datetime import datetime


class HISData(models.Model):
    """Synchronized data from HIS"""
    _name = 'hic.his.data'
    _description = 'HIS Synchronized Data'
    _order = 'last_sync desc'

    his_code = fields.Char('HIS Code', required=True, index=True)
    his_name = fields.Char('HIS Name', required=True)
    data_type = fields.Selection([
        ('medicine', 'Thuốc'),
        ('service', 'DVKT'),
        ('supply', 'VTYT'),
        ('department', 'Khoa phòng')
    ], required=True, index=True)
    his_price = fields.Float('HIS Price', digits=(15, 0))
    his_unit = fields.Char('HIS Unit')
    additional_info = fields.Text('Additional Info', help="JSON data from HIS")
    last_sync = fields.Datetime('Last Sync', default=fields.Datetime.now)
    active = fields.Boolean('Active', default=True)

    # ===== MAPPING STATUS =====
    is_mapped = fields.Boolean('Đã mapping', compute='_compute_mapping_status')
    mapped_to = fields.Char('Mapped to', compute='_compute_mapping_status')

    def action_create_mapping(self):
        pass

    def action_sync_single(self):
        pass

    def _compute_mapping_status(self):
        """Check if HIS data is mapped to BHYT"""
        for record in self:
            mapping_model = f'hic.{record.data_type}.mapping'
            if self.env[mapping_model].search([('his_data_id', '=', record.id)]):
                record.is_mapped = True
                # Get mapped BHYT item name
                mapping = self.env[mapping_model].search([('his_data_id', '=', record.id)], limit=1)
                bhyt_model = f'hic.{record.data_type}' if record.data_type != 'service' else 'hic.medical.service'
                bhyt_field = f'{record.data_type}_id' if record.data_type != 'service' else 'service_id'
                bhyt_record = getattr(mapping, bhyt_field)
                record.mapped_to = bhyt_record.display_name if bhyt_record else ''
            else:
                record.is_mapped = False
                record.mapped_to = ''

    @api.model
    def sync_from_his(self, data_type=None):
        """Sync data from HIS system"""
        # TODO: Implement actual HIS API integration
        # This is a placeholder for the sync logic

        if not data_type:
            # Sync all types
            for dtype in ['medicine', 'service', 'supply', 'department']:
                self._sync_data_type(dtype)
        else:
            self._sync_data_type(data_type)

    def _sync_data_type(self, data_type):
        """Sync specific data type from HIS"""
        # TODO: Implement actual API calls
        # Placeholder data for demo
        demo_data = {
            'medicine': [
                {'code': 'MED001', 'name': 'Paracetamol 500mg', 'price': 500, 'unit': 'Viên'},
                {'code': 'MED002', 'name': 'Amoxicillin 250mg', 'price': 800, 'unit': 'Viên'},
            ],
            'service': [
                {'code': 'SER001', 'name': 'Siêu âm bụng', 'price': 150000, 'unit': 'Lần'},
                {'code': 'SER002', 'name': 'Xét nghiệm máu', 'price': 80000, 'unit': 'Lần'},
            ],
            'supply': [
                {'code': 'SUP001', 'name': 'Băng gạc', 'price': 5000, 'unit': 'Cái'},
                {'code': 'SUP002', 'name': 'Kim tiêm', 'price': 2000, 'unit': 'Cái'},
            ],
            'department': [
                {'code': 'DEPT001', 'name': 'Khoa Nội', 'price': 0, 'unit': ''},
                {'code': 'DEPT002', 'name': 'Khoa Ngoại', 'price': 0, 'unit': ''},
            ]
        }

        for item in demo_data.get(data_type, []):
            existing = self.search([
                ('his_code', '=', item['code']),
                ('data_type', '=', data_type)
            ])

            vals = {
                'his_code': item['code'],
                'his_name': item['name'],
                'data_type': data_type,
                'his_price': item['price'],
                'his_unit': item['unit'],
                'last_sync': fields.Datetime.now(),
                'active': True
            }

            if existing:
                existing.write(vals)
            else:
                self.create(vals)


class HISWebhookLog(models.Model):
    """Log for HIS webhook calls"""
    _name = 'hic.his.webhook.log'
    _description = 'HIS Webhook Log'
    _order = 'create_date desc'

    name = fields.Char('Name', compute='_compute_name', store=True)
    webhook_type = fields.Selection([
        ('patient_admission', 'Patient Admission'),
        ('patient_discharge', 'Patient Discharge'),
        ('service_order', 'Service Order'),
        ('medication_order', 'Medication Order'),
        ('cost_generated', 'Cost Generated'),
    ], string='Webhook Type', required=True)

    # ===== REQUEST DATA =====
    request_data = fields.Text('Request Data', help="Raw JSON data from HIS")
    request_headers = fields.Text('Request Headers')
    request_ip = fields.Char('Request IP')

    # ===== PROCESSING RESULT =====
    status = fields.Selection([
        ('success', 'Success'),
        ('error', 'Error'),
        ('pending', 'Pending'),
    ], string='Status', default='pending')

    error_message = fields.Text('Error Message')
    processing_time = fields.Float('Processing Time (ms)')

    # ===== CREATED RECORDS =====
    claim_id = fields.Many2one('hic.claim', 'Created Claim')
    patient_id = fields.Many2one('his.patient', 'Patient')

    @api.depends('webhook_type', 'create_date')
    def _compute_name(self):
        for record in self:
            record.name = f"{record.webhook_type} - {record.create_date.strftime('%Y-%m-%d %H:%M:%S')}"

    @api.model
    def process_webhook(self, webhook_type, data, headers=None, request_ip=None):
        """Process incoming webhook from HIS"""
        start_time = datetime.now()

        # Create log entry
        log = self.create({
            'webhook_type': webhook_type,
            'request_data': json.dumps(data, indent=2),
            'request_headers': json.dumps(headers or {}, indent=2),
            'request_ip': request_ip,
            'status': 'pending'
        })

        try:
            # Process based on webhook type
            if webhook_type == 'cost_generated':
                result = self._process_cost_generated(data, log)
            elif webhook_type == 'patient_admission':
                result = self._process_patient_admission(data, log)
            else:
                raise ValidationError(f"Unsupported webhook type: {webhook_type}")

            # Update log with success
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            log.write({
                'status': 'success',
                'processing_time': processing_time,
            })

            return result

        except Exception as e:
            # Update log with error
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            log.write({
                'status': 'error',
                'error_message': str(e),
                'processing_time': processing_time,
            })
            raise

    def _process_cost_generated(self, data, log):
        """Process cost generation webhook - create/update claim"""
        patient_pid = data.get('patient_id')
        visit_id = data.get('visit_id')

        if not patient_pid or not visit_id:
            raise ValidationError("Missing patient_id or visit_id in webhook data")

        # Find or create patient
        patient = self.env['his.patient'].search([('patient_id', '=', patient_pid)], limit=1)
        if not patient:
            raise ValidationError(f"Patient not found: {patient_pid}")

        log.patient_id = patient.id

        # Check if patient can use BHYT
        if not patient.can_use_bhyt:
            raise ValidationError(f"Patient {patient_pid} cannot use BHYT")

        # Find existing claim or create new one
        claim = self.env['hic.claim'].search([('visit_id', '=', visit_id)], limit=1)

        if claim:
            # Update existing claim
            claim.action_sync_from_his()
        else:
            # Create new claim
            claim = self.env['hic.claim'].create_from_his_webhook(data)

        log.claim_id = claim.id
        return {'claim_id': claim.id, 'status': 'success'}

    def _process_patient_admission(self, data, log):
        """Process patient admission webhook"""
        # TODO: Implement admission processing
        return {'status': 'success'}

# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SyncHISWizard(models.TransientModel):
    _name = 'hic.sync.his.wizard'
    _description = 'Sync HIS Data Wizard'

    sync_type = fields.Selection([
        ('all', 'Tất cả'),
        ('medicine', 'Chỉ Thuốc'),
        ('service', 'Chỉ DVKT'),
        ('supply', 'Chỉ VTYT'),
        ('department', 'Chỉ Khoa phòng'),
    ], string='Loại đồng bộ', default='all', required=True)

    force_update = fields.Boolean(
        'Cập nhật ghi đè',
        default=False,
        help="Ghi đè dữ liệu đã có"
    )

    def action_sync(self):
        """Execute HIS sync"""
        self.ensure_one()
        
        try:
            if self.sync_type == 'all':
                data_types = ['medicine', 'service', 'supply', 'department']
            else:
                data_types = [self.sync_type]
            
            total_synced = 0
            for data_type in data_types:
                synced_count = self.env['hic.his.data']._sync_data_type(data_type)
                total_synced += synced_count
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Đồng bộ thành công'),
                    'message': _('Đã đồng bộ %s mục dữ liệu từ HIS') % total_synced,
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            raise UserError(_("Lỗi đồng bộ HIS: %s") % str(e))
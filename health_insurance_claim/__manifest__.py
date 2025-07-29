{
    'name': 'Health Insurance Claim (HIC)',
    'version': '18.0.1.0.0',
    'category': 'Healthcare',
    'summary': 'Health Insurance Claim Management System for BHYT',
    'description': """
        Health Insurance Claim Management System
        ========================================
        Quản lý hồ sơ giám định bảo hiểm y tế (BHYT)
        * Tích hợp với HIS để đồng bộ dữ liệu bệnh nhân và dịch vụ
        * Mapping danh mục BHYT-HIS (DVKT, Thuốc, VTYT, Khoa phòng)
        * Workflow giám định và gửi hồ sơ lên cổng BHYT
        * Tạo XML theo chuẩn Quyết định 4750/QĐ-BYT
    """,
    'author': 'Mate Technology JSC',
    'support': 'info@mate.com.vn',
    'website': 'https://mate.com.vn',
    'depends': ['his','his_base','account','mail'],
    'data': [
        'security/ir.model.access.csv',

        # Data
        'data/sequences.xml',

        # Views
        'views/patient_views.xml',
        'views/claim_views.xml',
        # 'views/claim_line_views.xml',
        'views/master_data_views.xml',
        'views/mapping_views.xml',

        # Menu
        'menu/menu.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 1,
    'license': 'LGPL-3',
}

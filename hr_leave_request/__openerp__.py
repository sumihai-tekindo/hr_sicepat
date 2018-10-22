# -*- coding: utf-8 -*-
# © 2016, Dedi Sinaga <dedi@sicepat.com>
# © 2016 Sumihai Teknologi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'HR Leave Request',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'author': 'Ade Anugerah',
    'website': "https://github.com/sumihai-tekindo/",
    'depends': [
        'base',
        'hr',
        'account',
        'hr_payroll',
        'hr_nik',
        'hr_salary_add',
    ],
    'data': [     
        'security/hr_leave_request_access.xml',
        'views/hr_leave_workflow.xml',
        'views/allocation_valid_periode.xml',
        'views/add_desc_leave_type.xml',
        'views/hr_category_master.xml',
        'views/hr_leave_request.xml',
        'views/allocation_request_inherit_onchange.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}

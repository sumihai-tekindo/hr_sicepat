# -*- coding: utf-8 -*-
# © 2016, Dedi Sinaga <dedi@sicepat.com>
# © 2016 Sumihai Teknologi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'HR Payroll Template',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'author': 'Ade Anugerah',
    'website': "https://github.com/sumihai-tekindo/",
    'depends': [
        'hr',
        'hr_payroll',
        'hr_payroll_account',
        'hr_attendance_payslip'
    ],
    'data': [     
        'views/department_struct_ids.xml',
        'views/hr_wizard_template.xml',
        'views/is_template_rule.xml',
        'views/is_template_structure.xml',
        'views/hr_job_position.xml',
        'views/hr_job_code.xml',
    ],
    'installable': True,
}

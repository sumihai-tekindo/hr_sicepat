# -*- coding: utf-8 -*-
# © 2016, Dedi Sinaga <dedi@sicepat.com>
# © 2016 Sumihai Teknologi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'HR Education Cost',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'author': 'Ade Anugerah',
    'website': "https://github.com/sumihai-tekindo/",
    'depends': [
        'hr',
        'account',
        'analytic',
        'hr_payroll',
        'hr_payroll_account',
        'hr_nik',
        'hr_attendance_payslip',
        'hr_salary_add',
    ],
    'data': [     
        'data/hr_education_cost.xml',
        'views/hr_education_cost.xml',
        'security/ir.model.access.csv',
        'security/hr_education_access.xml',
    ],
    'installable': True,
}

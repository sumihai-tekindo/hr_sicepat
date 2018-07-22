# -*- coding: utf-8 -*-
# © 2016, Dedi Sinaga <dedi@sicepat.com>
# © 2016 Sumihai Teknologi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Payslip Reports',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'author': 'Dedi Sinaga',
    'website': 'dedisinaga.blogspot.com',
    'description': """This modules provide Payslip Reports""",
    'depends': ['hr','hr_payroll','hr_attendance','hr_attendance_payslip','report_xls','report'],
    'data': [
        'reports/change_footer.xml',
        'views/department_payslip_view.xml',
        'views/hr_contact_setting.xml',
        'reports/department_payslip_report.xml',
        'reports/employee_payslip.xml',
    ],
    'installable': True,
}

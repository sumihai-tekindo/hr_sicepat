# -*- coding: utf-8 -*-
{
    'name': "E-mail Payslip",
    'summary': """Send payslips via e-mail""",
    'description': """
            module that sends payslips to the owner employees via e-mail
    """,

    'author': "Ade Anugerah",
    'website': "https://github.com/sumihai-tekindo/",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'hr_payroll', 'report', 'hr_salary_add'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_payslip_email.xml',
        'views/hr_contact_in_company.xml',
        'datas/email_payslip_template.xml',
    ],
}
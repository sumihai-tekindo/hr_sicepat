# -*- coding: utf-8 -*-
{
    'name': "hr_salary_add",

    'summary': "Courses, Sessions, Subscriptions",

    'description': "...",

    'author': "Your Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Tools',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['account', 'analytic', 'hr_payroll'],

    # always loaded
    'data': ["views/hr_salary_particular_view.xml","views/hr_delivery_package_view.xml","views/hr_overtime_view.xml"
             ,"views/hr_insentif_view.xml","views/hr_employee_mutation_view.xml","views/hr_memorandum_view.xml",
             "views/hr_promotion_view.xml","views/hr_salary_proposal_view.xml","views/hr_loan_view.xml",
             "data/hr_loan_sequence.xml",
             "data/delivery_package_sequence.xml",
             "data/hr_employee_mutation_sequence.xml",
             "data/hr_insentif_sequence.xml",
             "data/hr_memorandum_sequence.xml",
             "data/hr_overtime_sequence.xml",
             "data/hr_promotion_sequence.xml",
             "data/hr_salary_particular_sequence.xml",
             "data/hr_salary_proposal_sequence.xml"],
    # only loaded in demonstration mode
    'demo': [],
    'images': [],
    'application': True,
}
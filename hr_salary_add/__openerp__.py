# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Sicepat Ekspres Indonesia (<http://www.sicepat.com>).
#    @author: - Timotius Wigianto <https://github.com/timotiuswigianto/>
#             - Dedi Sinaga <dedisinaga@gmail.com>
#             - Pambudi Satria <pambudi.satria@yahoo.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': "HR Sicepat Ekspres",

    'summary': "HR for Sicepat Ekspres Indonesia",

    'description': """
==================
HR Sicepat Ekspres
==================



    """,

    'author': 'Timotius Wigianto, '
              'Dedi Sinaga, '
              'Pambudi Satria',
    'website': "https://github.com/sumihai-tekindo/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'sequence': 2,
    'version': '8.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'account',
        'analytic',
        'hr_payroll',
        'hr_payroll_account',
    ],

    # always loaded
    'data': [
        "views/hr_employee_view.xml",
        "views/hr_payroll_view.xml",
        "views/hr_salary_structure_amt_view.xml",
        "views/hr_delivery_package_view.xml",
        "views/hr_overtime_view.xml",
        "views/hr_insentif_view.xml",
        "views/hr_employee_mutation_view.xml",
        "views/hr_memorandum_view.xml",
        "views/hr_promotion_view.xml",
        "views/hr_salary_proposal_view.xml",
        "views/hr_loan_view.xml",
        "data/hr_salary_structure_amt_seq.xml",
        "data/hr_loan_sequence.xml",
        "data/delivery_package_sequence.xml",
        "data/hr_employee_mutation_sequence.xml",
        "data/hr_insentif_sequence.xml",
        "data/hr_memorandum_sequence.xml",
        "data/hr_overtime_sequence.xml",
        "data/hr_promotion_sequence.xml",
        "data/hr_salary_proposal_sequence.xml",
        "views/pengiriman_paket.xml",
        "views/hr_employee_resign.xml"],
    # only loaded in demonstration mode
    'demo': [],
    'images': [],
    'qweb': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'post_init_hook': 'populate_jabatan_department_loan',
}
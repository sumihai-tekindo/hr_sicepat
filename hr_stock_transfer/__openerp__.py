# -*- coding: utf-8 -*-
# © 2016, Dedi Sinaga <dedi@sicepat.com>
# © 2016 Sumihai Teknologi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'HR Stock Transfer',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Stock',
    'author': 'Dedi Sinaga',
    'website': 'dedisinaga.blogspot.com',
    'description': """This modules provide Stock Transfer information connected to Employee Loan""",
    'depends': ['stock','stock_account','hr_salary_add','stock_analytic_account'],
    'data': [
        'views/stock_move_view.xml',
    ],
    'installable': True,
}

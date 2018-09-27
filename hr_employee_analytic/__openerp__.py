{
    'name': 'HR Employee Analytic',
    'version': '8.0.1.0.0',
    'summary': """
     Merge HR Contract & Employee)
    """,
    'license': 'AGPL-3',

    'category': 'Generic Modules/Human Resources',
    'author': 'Aditya',
    'depends': [
        'hr_salary_add',
    ],
    'data': [     
        'views/employee.xml',
    ],
    'installable': True,
}
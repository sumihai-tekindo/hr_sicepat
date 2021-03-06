# -*- coding: utf-8 -*-
# © 2011, 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'NIK',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'author': 'Michael Telahun Makonnen, '
              'OpenSynergy Indonesia,'
              'Odoo Community Association (OCA)',
    'website': 'http://miketelahun.wordpress.com',
    'depends': [
        'hr',
    ],
    'data': [
        'views/res_config_views.xml',
        'views/res_company.xml',
        'views/hr_employee_views.xml',
        'data/hr_employee_sequence.xml',
    ],
    'installable': True,
}

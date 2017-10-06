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
    'name': "EMP Recruitment",

    'summary': "EMP Recruitment for Sicepat Ekspres Indonesia",

    'description': """
==================
HR Sicepat Ekspres
==================



    """,

    'author': 'Derri Widardi',
    'website': "https://github.com/sumihai-tekindo/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'sequence': 2,
    'version': '8.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'hr',
    ],

    # always loaded
    'data': [
        "views/emp_recruitment_view.xml",
        "views/emp_recruitment_level_view.xml",
        "views/emp_recruitment_agama_view.xml",
        "views/emp_recruitment_bahasa_view.xml",
        "views/emp_recruitment_pendidikan_view.xml",
        "views/emp_recruitment_skill_view.xml",
        "views/emp_recruitment_sumber_view.xml",
        "views/emp_form.xml"
        
        ],
    
}
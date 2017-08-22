# -*- coding: utf-8 -*-
##############################################################################
#
#    @author: - Pambudi Satria <pambudi.satria@yahoo.com>
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
    'name': "BPJS",
    'summary': "Badan Penyelenggara Jaminan Sosial",
    'author': 'Pambudi Satria',
    'website': 'https://bitbucket.org/pambudisatria/',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'hr_payroll',
    ],

    # always loaded
    'data': [
        'data/bpjs_data.xml',
        'security/ir.model.access.csv',
        'views/bpjs_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'images': [],
    'qweb': [],
    'installable': True,
    'application': True,
}
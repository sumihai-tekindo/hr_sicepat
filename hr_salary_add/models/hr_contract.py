# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017 Sicepat Ekspres Indonesia (<http://www.sicepat.com>).
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

# 1 : imports of python lib

# 2 :  imports of openerp
from openerp.osv import fields, osv

# 3 :  imports from odoo modules

class hr_contract(osv.osv):
    # Private attributes
    _inherit = 'hr.contract'

    # Default methods
    

    # Fields declaration
    _columns = {
            'department_id': fields.many2one('hr.department', 'Department', required=True),
        }

    # compute and search fields, in the same order that fields declaration

    # Constraints and onchanges
    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        if not employee_id:
            return {'value': {'job_id': False, 'department_id': False}}
        emp_obj = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
        job_id = False
        department_id = False
        if emp_obj.job_id:
            job_id = emp_obj.job_id.id
        if emp_obj.department_id:
            department_id = emp_obj.department_id.id
        return {'value': {'job_id': job_id, 'department_id': department_id}}

    # CRUD methods

    # Action methods

    # Business methods

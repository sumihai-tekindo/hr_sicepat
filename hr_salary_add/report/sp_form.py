#-*- coding:utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp.osv import osv
from openerp.report import report_sxw


class sp_form(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(sp_form, self).__init__(cr, uid, name, context)
        self.localcontext.update({
        	'get_type_sp': self._get_type_sp,
        	'get_type': self._get_type,
        	})
    
    def _get_type_sp(self):
    	type_ids = self.pool.get("hr.memorandum.type").search(self.cr, self.uid,[])
    	result = self.pool.get("hr.memorandum.type").browse(self.cr, self.uid, type_ids)
    	return result

    def _get_type(self,type,type_sp):

    	if type.id==type_sp.id:
	    	print("type:%s"%type)
	    	print("type_sp:%s"%type_sp)
    		return True
    	print("salah")
    	return False


class wrapped_form_sp(osv.AbstractModel):
    _name = 'report.hr_salary_add.sp_form'
    _inherit = 'report.abstract_report'
    _template = 'hr_salary_add.sp_form'
    _wrapped_report_class = sp_form

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

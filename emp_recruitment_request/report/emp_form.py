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


class emp_form(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(emp_form, self).__init__(cr, uid, name, context)
        self.localcontext.update({
        	'get_level_id': self._get_level_id,
        	'get_level': self._get_level,
        	})
    
    def _get_level_id(self):
    	level_ids = self.pool.get("emp.recruitment.level").search(self.cr, self.uid,[])
    	result = self.pool.get("emp.recruitment.level").browse(self.cr, self.uid, level_ids)
    	return result

    def _get_level(self,type,level_id):

    	if type.id==level_id.id:
	    	print("level:%s"%type)
	    	print("level_id:%s"%level_id)
    		return True
    	print("salah")
    	return False


class wrapped_emp_form(osv.AbstractModel):
    _name = 'report.emp_recruitment_request.emp_form'
    _inherit = 'report.abstract_report'
    _template = 'emp_recruitment_request.emp_form'
    _wrapped_report_class = emp_form

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

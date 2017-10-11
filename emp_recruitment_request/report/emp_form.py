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
            'get_agama_id': self._get_agama_id,
            'get_agama': self._get_agama,
            'get_b_id': self._get_b_id,
            'get_b': self._get_b,
            'get_sumber_id': self._get_sumber_id,
            'get_sumber': self._get_sumber,
            'get_pendidikan_id': self._get_pendidikan_id,
            'get_pendidikan': self._get_pendidikan,
            'get_stat_id': self._get_stat_id,
            'get_stat': self._get_stat,
            'get_skill_id': self._get_skill_id,
            'get_skill': self._get_skill,
        	})

    def _get_level_id(self):
    	level_ids = self.pool.get("emp.recruitment.level").search(self.cr, self.uid,[])
    	result = self.pool.get("emp.recruitment.level").browse(self.cr, self.uid, level_ids)
    	return result

    def _get_level(self,type,level_id):

    	if type.id==level_id.id:
    		return True
    	return False

    def _get_agama_id(self):
        agama_ids = self.pool.get("emp.recruitment.agama").search(self.cr, self.uid,[])
        result = self.pool.get("emp.recruitment.agama").browse(self.cr, self.uid, agama_ids)
        return result

    def _get_agama(self,type,agama_id):

        if type.id==agama_id.id:
            return True
        return False

    def _get_b_id(self):
        b_ids = self.pool.get("emp.recruitment.b").search(self.cr, self.uid,[])
        result = self.pool.get("emp.recruitment.b").browse(self.cr, self.uid, b_ids)
        return result

    def _get_b(self,type,b_id):

        if type.id==b_id.id:
            return True
        return False

    def _get_sumber_id(self):
        sumber_ids = self.pool.get("emp.recruitment.sumber").search(self.cr, self.uid,[])
        result = self.pool.get("emp.recruitment.sumber").browse(self.cr, self.uid, sumber_ids)
        return result

    def _get_sumber(self,type,sumber_id):

        if type.id==sumber_id.id:
            return True
        return False

    def _get_pendidikan_id(self):
        pendidikan_ids = self.pool.get("emp.recruitment.pendidikan").search(self.cr, self.uid,[])
        result = self.pool.get("emp.recruitment.pendidikan").browse(self.cr, self.uid, pendidikan_ids)
        return result

    def _get_pendidikan(self,type,pendidikan_id):

        if type.id==pendidikan_id.id:
            return True
        return False

    def _get_stat_id(self):
        stat_ids = self.pool.get("emp.recruitment.stat").search(self.cr, self.uid,[])
        result = self.pool.get("emp.recruitment.stat").browse(self.cr, self.uid, stat_ids)
        return result

    def _get_stat(self,type,stat_id):

        if type.id==stat_id.id:
            return True
        return False

    def _get_skill_id(self):
        skill_ids = self.pool.get("emp.recruitment.skill").search(self.cr, self.uid,[])
        result = self.pool.get("emp.recruitment.skill").browse(self.cr, self.uid, skill_ids)
        return result

    def _get_skill(self,type,skill_id):

        if type.id==skill_id.id:
            return True
        return False

class wrapped_emp_form(osv.AbstractModel):
    _name = 'report.emp_recruitment_request.emp_form'
    _inherit = 'report.abstract_report'
    _template = 'emp_recruitment_request.emp_form'
    _wrapped_report_class = emp_form

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

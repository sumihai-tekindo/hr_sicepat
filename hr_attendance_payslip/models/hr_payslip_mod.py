# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import AccessError, Warning

class HRPayslip(models.Model):
	_inherit = "hr.payslip"

	def onchange_employee_id(self, cr, uid, ids, date_from, date_to, employee_id=False, contract_id=False, context=None):
		res = super(HRPayslip,self).onchange_employee_id(cr, uid, ids, date_from, date_to, employee_id=employee_id, contract_id=contract_id, context=context)
		if res:
			contract_id = res.get('value', {}) and res.get('value').get('contract_id', False)
			if contract_id:
				contract = self.pool.get('hr.contract').browse(cr, uid, [contract_id], context=context)
				if contract.date_start and contract.date_start >= date_from:
					date_from = contract.date_start
				if contract.date_end and contract.date_end <= date_to:
					date_to = contract.date_end
				attendance_ids = self.pool.get('hr.attendance').search(cr,uid,[('employee_id','=',employee_id),('action','=','sign_out'),('name','>=',date_from),('name','<=',date_to)])
				if attendance_ids:
					attendances = self.pool.get('hr.attendance').browse(cr,uid,attendance_ids)
					attendance_total = len(attendance_ids)
					total_hours = 0.0
					for att in attendances:
						total_hours+=att.worked_hours
					value = {
						'name': 'Sign in & Sign Out Attendances',
						'code': 'SISO',
						'number_of_days': attendance_total or 0.0,
						'number_of_hours': total_hours or 0.0,
						'contract_id': contract.id,
					}
					old = res.get('value',{})
					old_worked_lines = old.get('worked_days_line_ids',[])
					old_worked_lines.append(value)
					old.update({'worked_days_line_ids':old_worked_lines})
					res.update({'value':old})
					return res
		return res
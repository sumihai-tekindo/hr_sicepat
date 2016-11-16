# -*- coding: utf-8 -*-
from openerp.osv import osv, fields 

class hr_payslip(osv.osv):
	_inherit = "hr.payslip"

	def onchange_employee_id(self, cr, uid, ids, date_from, date_to, employee_id=False, contract_id=False, context=None):
		old_change = super(hr_payslip,self).onchange_employee_id(cr, uid, ids, date_from, date_to, employee_id=employee_id, contract_id=contract_id, context=context)
		if employee_id and date_from and date_to and contract_id:
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
					'contract_id': contract_id or False,
					}
				old = old_change.get('value',{})
				old_worked_lines = old.get('worked_days_line_ids',[])
				old_worked_lines.append(value)
				old.update({'worked_days_line_ids':old_worked_lines})
				return {'value':old}
		return old_change
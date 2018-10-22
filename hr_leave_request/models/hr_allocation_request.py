from openerp import api, fields, models, _
from openerp.exceptions import ValidationError, Warning

class hr_holidays(models.Model):
	_inherit = "hr.holidays"

	valid_periode = fields.Date('Valid Date')

	def _check_date(self, cr, uid, ids, context=None):
		for holiday in self.browse(cr, uid, ids, context=context):
			domain = [
				('date_from', '<=', holiday.date_to),
				('date_to', '>=', holiday.date_from),
				('employee_id', '=', holiday.employee_id.id),
				('id', '!=', holiday.id),
				('state', 'not in', ['cancel', 'refuse']),
				('holiday_status_id', '=', holiday.holiday_status_id.id),
				('type', '=', holiday.type),
			]
			nholidays = self.search_count(cr, uid, domain, context=context)
			if nholidays:
				return False
		return True

	_check_holidays = lambda self, cr, uid, ids, context=None: self.check_holidays(cr, uid, ids, context=context)

	_constraints = [
		(_check_date, 'You can not have 2 leaves that overlaps on same day!', ['date_from','date_to']),
		(_check_holidays, 'The number of remaining leaves is not sufficient for this leave type', ['state','number_of_days_temp'])
	] 

	@api.model
	def default_get(self, fields):
		res = super(hr_holidays, self).default_get(fields)
		
		if res.get('type'):
			if res['type'] == 'add' and res['employee_id']:
				res['employee_id'] = False

		return res

	def onchange_date_from(self, cr, uid, ids, date_to, date_from, context=None):
		res = super(hr_holidays, self).onchange_date_from(cr, uid, ids, date_to, date_from)

		if context.get('default_type') and context.get('default_type') == 'add':
			res = {'value': {}}
			return res
		
		return res

	def onchange_date_to(self, cr, uid, ids, date_to, date_from, context=None):
		res = super(hr_holidays, self).onchange_date_to(cr, uid, ids, date_to, date_from)

		if context.get('default_type') and context.get('default_type') == 'add':
			res = {'value': {'valid_periode': date_to}}
			return res
		
		return res

	@api.onchange('holiday_status_id')
	def onchange_leave_type(self):
		if self.type == 'add' and self.holiday_status_id:
			leave_type = self.env['hr.category.master'].search([('leave_type', 'in', [self.holiday_status_id.id] )])
			if leave_type and self.holiday_type == 'employee':
				if self.employee_id:
					employee = self.env['hr.employee'].search([('id', '=', self.employee_id.id)])
					if employee.company_id:
						if self.holiday_status_id.limit == False:
							self.valid_periode = employee.company_id.leave_end_periode
						else:
							result = self.pool["hr.holidays"].onchange_date_to(self._cr, self._uid, [self.id], self.date_to, self.date_from, context=self._context)
							self.valid_periode = result.get('value').get('valid_periode')
							
					for levtype in leave_type:
						if employee.job_id.id in [job.id for job in levtype.job_ids]:
							if levtype.gender != 'all' and employee.gender != levtype.gender:
								self.number_of_days_temp = 0.00
								return {'warning': {
									'message':_('you cannot pick this leave_type'),
									'title': _('Validation Error')
									}} 
							else:
								self.number_of_days_temp = levtype.number_of_days + employee.remaining_leaves
								break

			elif leave_type and self.holiday_type == 'category':
				for ltype in leave_type:
					if ltype.leave_tag.id == self.category_id.id:
						self.number_of_days_temp = ltype.number_of_days
						break
					else:
						self.number_of_days_temp = 0.00

	def onchange_employee(self, cr, uid, ids, employee_id, holiday_status_id=False, context=None):
		category_master = self.pool.get('hr.category.master')
		leave_type = ''
		if holiday_status_id:
			leave_type_ids = category_master.search(cr, uid, [('leave_type', 'in', [holiday_status_id])])
			if not leave_type_ids:
				raise ValidationError(_('Leave type undefined'))
			leave_type = category_master.browse(cr, uid, leave_type_ids)

		if employee_id:
			res = super(hr_holidays, self).onchange_employee(cr, uid, ids, employee_id)
			employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)
			if leave_type and employee:
				for levtype in leave_type:
					if employee.job_id.id in [job.id for job in levtype.job_ids]:
						if levtype.gender == 'all' or employee.gender == levtype.gender:
							res['value'].update({'number_of_days_temp': levtype.number_of_days})
						else:
							raise ValidationError(_('you cannot pick this leave_type'))
			return res

	@api.onchange('category_id')
	def onchange_category_id(self):
		if self.category_id:
			leave_type = self.env['hr.category.master'].search([('leave_type', 'in', [self.holiday_status_id.id] )])
			for ltype in leave_type:
				if ltype.leave_tag.id == self.category_id.id:
					self.number_of_days_temp = ltype.number_of_days
					break
				else:
					self.number_of_days_temp = 0.00
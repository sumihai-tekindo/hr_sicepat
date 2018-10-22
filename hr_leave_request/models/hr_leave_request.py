from openerp import api, fields, models, _
from openerp.exceptions import ValidationError, Warning
from datetime import datetime, timedelta
from openerp import tools
import math
from openerp.addons.hr_holidays.hr_holidays import hr_holidays as hr_holidays_super_model
from openerp import SUPERUSER_ID


class LeaveCategoryMaster(models.Model):
	_name = 'hr.category.master'

	leave_type    		  = fields.Many2one('hr.holidays.status', string='Leave Type', required=True)
	name                  = fields.Char(string="Description", required=True) 
	number_of_days 		  = fields.Float(string='Number Of Days')
	leave_tag	  		  = fields.Many2many('hr.employee.category', string='Leave Tag')
	gender                = fields.Selection([
								('male', "Male"),
								('female', "Female"),
								('all', "All"),
							], default='all')
	job_ids       	      = fields.Many2many('hr.job', required=True)


class hr_holidays_status(models.Model):
	_inherit = "hr.holidays.status"

	description = fields.Boolean(default=False, readonly=True)

	def get_days(self, cr, uid, ids, employee_id, context=None):
		result = dict((id, dict(max_leaves=0, leaves_taken=0, remaining_leaves=0,
								virtual_remaining_leaves=0, current_leave=0, max_leaves_past_year=0)) for id in ids)
		holiday_ids = self.pool['hr.holidays'].search(cr, uid, [('employee_id', '=', employee_id),
																('state', 'in', ['confirm', 'validate1', 'validate']),
																('holiday_status_id', 'in', ids)
																], context=context)
		current_year = datetime.today().strftime('%Y-%m-%d')

		for holiday in self.pool['hr.holidays'].browse(cr, uid, holiday_ids, context=context):
			status_dict = result[holiday.holiday_status_id.id]
			if holiday.type == 'add':
				if holiday.valid_periode > current_year:
					status_dict['virtual_remaining_leaves'] += holiday.number_of_days_temp
					if holiday.state == 'validate':
						status_dict['max_leaves'] += holiday.number_of_days_temp
						status_dict['remaining_leaves'] += holiday.number_of_days_temp
						if current_year >= holiday.date_from and current_year <= holiday.date_to:
							status_dict['current_leave'] += holiday.number_of_days_temp
						if holiday.date_to < current_year:
							status_dict['max_leaves_past_year'] += holiday.number_of_days_temp
					
			elif holiday.type == 'remove':  # number of days is negative
				status_dict['virtual_remaining_leaves'] -= holiday.number_of_days_temp
				if holiday.state == 'validate':
					status_dict['leaves_taken'] += holiday.number_of_days_temp
					status_dict['remaining_leaves'] -= holiday.number_of_days_temp
					if not holiday.max_leaves_past_year:
						status_dict['current_leave'] -= holiday.number_of_days_temp
					else:
						status_dict['max_leaves_past_year'] -= holiday.number_of_days_temp
					status_dict['max_leaves'] -= holiday.number_of_days_temp
		
		return result


class hr_holidays(models.Model):
	_inherit = "hr.holidays"


	@api.depends('employee_id', 'employee_id.user_id')
	def _get_can_reset(self):
		self.can_reset = False
		if self.user_has_groups('hr_leave_request.leave_request_approval'):
			self.can_reset = True

		if self.employee_id and self.employee_id.user_id and self.employee_id.user_id.id == self.env.uid:
			self.can_reset = True		

	@api.multi
	def write(self, vals):
		employee_id = vals.get('employee_id', False)
		if vals.get('state') and vals['state'] not in ['draft', 'confirm', 'cancel'] and not self.pool['res.users'].user_has_groups(self._cr, self._uid, 'hr_leave_request.leave_request_approval'):
			raise Warning(_('You cannot set a leave request as \'%s\'. Contact a human resource manager.') % vals.get('state'))

		res = models.Model.write(self, vals)
		self.add_follower(employee_id, context=self._context)
		return res

	can_reset = fields.Boolean(compute="_get_can_reset")
	total_days_according_to_categories = fields.Float(string='Total Days of Categories', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]})
	employee_email = fields.Char(string="Email", readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]})
	employee_contact_number = fields.Char(string="Contact Number", readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]})
	current_leave = fields.Float(string='Hak Cuti Tahun Berjalan', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]})
	max_leaves_past_year = fields.Float(string='Sisa Cuti Tahun Sebelumnya', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]})
	max_leaves = fields.Float(string='Total Cuti', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]})
	remaining_leaves = fields.Float(string='Akumulasi Sisa Cuti', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]})
	description = fields.Boolean(related="holiday_status_id.description")
	assign_to = fields.Many2one('hr.employee', string="Temporary Employees During The Period", help='Temporary Employees who can handle Task, this fields is assign by manager.', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]})

	def onchange_date_to(self, cr, uid, ids, date_to, date_from):
		result = super(hr_holidays, self).onchange_date_to(cr, uid, ids, date_to=date_to, date_from=date_from)
		if date_from and date_to:
			new_dt_from = datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S')
			new_dt_to = datetime.strptime(date_to, '%Y-%m-%d %H:%M:%S')
			employee_id= self.pool.get('hr.employee').search(cr,uid,[('user_id', '=', uid)])
			employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)
			working_hours_id = employee.contract_id.working_hours.id
			working_hours_of_date = self.pool.get('resource.calendar').get_working_hours(cr, SUPERUSER_ID, working_hours_id, new_dt_from, new_dt_to)
			if working_hours_of_date:
				result['value']['number_of_days_temp'] = round(math.floor(working_hours_of_date / 8 )) + 1

		return result

	@api.onchange('holiday_status_id', 'number_of_days_temp')
	def onchange_leave_type_request(self):
		if self.type == 'remove' and self.holiday_status_id:
			self.remaining_leaves = 0.00
			self.valid_periode = False

			if not self.description:
				self.name = ''

			leave_type = self.env['hr.category.master'].search([('leave_type', 'in', [self.holiday_status_id.id] )])
			if leave_type and self.holiday_type == 'employee':
				employee= self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
				if employee:
					self.employee_id = employee.id
					days_obj = self.pool['hr.holidays.status'].get_days(self._cr, self._uid, [self.holiday_status_id.id], employee.id)
					remaining_leaves_emp = [days_obj[val]['remaining_leaves'] for val in days_obj]
					remaining_leaves_emp_val = remaining_leaves_emp[0] if remaining_leaves_emp else 0

					year_from = datetime.today().strftime('%Y-01-01')
					year_to = datetime.today().strftime('%Y-12-31')

					domain = [ ('type', '=', 'remove'),
							   ('state', '=', 'validate'), 
							   ('holiday_status_id', '=', self.holiday_status_id.id),
							   ('holiday_status_id.limit', '=', True),
							   ('date_to', '>=', year_from),
							   ('date_to', '<=', year_to)
							  ]
					special_leaves = self.search(domain)
					for key in days_obj:
						if special_leaves:
							self.max_leaves = 0
							self.current_leave = 0
							self.max_leaves_past_year = 0
						else:
							self.max_leaves = days_obj[key]['max_leaves']
							self.current_leave = days_obj[key]['current_leave']
							self.max_leaves_past_year = days_obj[key]['max_leaves_past_year']

					if self.number_of_days_temp:
						if self.holiday_status_id.id != 1 and not self.max_leaves:
							self.remaining_leaves = 0
						else: 
							self.remaining_leaves = self.max_leaves - self.number_of_days_temp

					for levtype in leave_type:
						if employee.job_id.id in [job.id for job in levtype.job_ids]:
							x = levtype.number_of_days / 2
							if self.remaining_leaves < 0 and self.remaining_leaves + x < 0:
								return {'warning': {
									'message':_('minus leave exceeds the allowable limit'),
									'title': _('Validation Error')
									}} 

							if levtype.gender != 'all' and employee.gender != levtype.gender:
								self.total_days_according_to_categories = 0.00
								return {'warning': {
									'message':_('you cannot pick this leave_type'),
									'title': _('Validation Error')
									}} 
							else: 
								self.total_days_according_to_categories = levtype.number_of_days
								break

	@api.constrains('remaining_leaves', 'holiday_status_id')
	def _constrain(self):
		leave_type = self.env['hr.category.master'].search([('leave_type', 'in', [self.holiday_status_id.id] )])
		employee= self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
		for levtype in leave_type:
			if employee.job_id.id in [job.id for job in levtype.job_ids]:
				x = levtype.number_of_days / 2
				if self.remaining_leaves < 0 and self.remaining_leaves + x < 0:
					raise ValidationError(_('minus leave exceeds the allowable limit'))

				if levtype.gender != 'all' and employee.gender != levtype.gender:
					raise ValidationError(_('you cannot pick this leave_type'))


class ResCompany(models.Model):
	_inherit = 'res.company'

	leave_end_periode = fields.Date(string="Valid Periode for leaves")

class hr_employee(models.Model):
	_inherit="hr.employee"

	@api.one
	def _get_remaining_days(self):
		self.ensure_one()
		holidays_ids = self.env['hr.holidays'].search([('employee_id', '=', self.id)] )
		holiday_status_id = self.env['hr.holidays.status'].search([('id', 'in', [id_status.holiday_status_id.id for id_status in holidays_ids]), ('limit', '=', False)])
		res = self.pool['hr.holidays.status'].get_days(self._cr, self._uid, [holiday_status_id.id], self.id)

		remaining = sum([value['remaining_leaves'] for key, value in res.items() if key == 1])

		for employee in self:
			employee.remaining_leaves = remaining

	remaining_leaves = fields.Float(compute='_get_remaining_days',  fnct_inv='_set_remaining_days')

from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import api, fields, models, _
from openerp.addons.base.ir.ir_cron import _intervalTypes
import time

class hr_employee(models.Model):
	_inherit = "hr.employee"
	_order = "end_date desc" 

	@api.depends('contract_ids.date_end',
				'contract_ids.date_start',
				'contract_ids.working_hours',
				'contract_ids.sts_karyawan',
				'contract_ids.promotion_trial',
				'contract_ids.job_id_trial',
				'contract_ids.trial_date_start',
				'contract_ids.trial_date_end')
	@api.multi
	def get_detail_contract(self):
		for employee in self :
			contract_id = employee.contract_id

			if contract_id.date_end and contract_id.sts_karyawan!='kartap':
				days_left=datetime.strptime(str(contract_id.date_end),'%Y-%m-%d')-datetime.today()
				employee.days_left=str(days_left.days)

			if contract_id.sts_karyawan =='kartap':	
				employee.days_left= -1

			if contract_id.sts_karyawan =='ojt':
				employee.start_date = contract_id.trial_date_start
				employee.end_date = contract_id.trial_date_end	

	work_location_analytic = fields.Many2one('account.analytic.account','Work Location')
	working_hour = fields.Many2one('resource.calendar','Working Schedule')
	end_date = fields.Date('Contract End')
	start_date = fields.Date('Contract Start')
	today=fields.Date('Date Diff',default=fields.Date.today)
	days_left = fields.Integer('Warning Date',compute='get_detail_contract')
	sts_karyawan = fields.Selection([
				('ojt','On The Job Training'),
				('kontrak','Kontrak'),
				('kartap','Karyawan Tetap'),
			], string='Employee Status')
	promotion_trial=fields.Boolean('Promotion')
	job_id_trial = fields.Many2one('hr.job','Job Title Trial')

	@api.onchange('work_location_analytic') 
	def check_change(self):
		if self.work_location_analytic:
			self.work_location = self.work_location_analytic.name

class hr_contract(models.Model):
	_inherit = "hr.contract" 
	
	@api.model		
	def _execute_contract(self):		
		today = time.strftime('%Y-%m-%d')
		# search contract start date = today
		contract_ids = self.env['hr.contract'].search([('date_start','=',today)])
		for contract in contract_ids :
				
					date_start = datetime.strptime(contract.date_start,'%Y-%m-%d').strftime('%Y-%m-%d')
					if contract.promotion_trial:
						# print"promotion========================================"
						contract.employee_id.write({'department_id':contract.department_trial.id,
												'job_id_trial':contract.job_id_trial.id,
												'sts_karyawan': contract.sts_karyawan,
												'job_id':contract.job_id.id,
												'promotion_trial':contract.promotion_trial,
												'start_date':contract.date_start,
												'end_date': contract.date_end,
												'working_hour':contract.working_hours.id
											})
					else:
						# print"non promotion========================================",contract.date_start
						contract.employee_id.write({'department_id':contract.department_id.id,
												'job_id':contract.job_id.id,
												'sts_karyawan': contract.sts_karyawan,
												'job_id_trial':contract.job_id_trial.id,
												'promotion_trial':contract.promotion_trial,
												'start_date':contract.date_start,
												'end_date': contract.date_end,
												'working_hour':contract.working_hours.id
											})	
									
	promotion_trial=fields.Boolean(string='Promotion Trial', default=False)
	promotion_start_date=fields.Date('Promotion Start Date')
	promotion_end_date=fields.Date('Promotion End Date')
	department_trial=fields.Many2one('hr.department','Department Trial')
	job_id_trial = fields.Many2one('hr.job')
	sts_karyawan = fields.Selection([
			('ojt','On The Job Training'),
			('kontrak','Kontrak'),
			('kartap','Karyawan Tetap'),
		], string='Employee Status',required=True)

	@api.onchange('job_id_trial','promotion_trial','department_trial','promotion_end_date','promotion_start_date','trial_date_start','trial_date_end')  
	def check_change(self):

		if self.department_trial:
			self.department_id = self.department_trial
		if self.promotion_start_date:
			self.date_start = self.promotion_start_date	
		if self.promotion_end_date:
			self.date_end = self.promotion_end_date		
		if self.trial_date_start:
			self.date_start = self.trial_date_start
		if self.trial_date_end:
			self.date_end = self.trial_date_end
	
		if self.promotion_trial==False:
			self.job_id_trial=False	
			self.department_trial=False	
			self.promotion_start_date=False	
			self.promotion_end_date=False
		else :
			self.date_start = self.promotion_start_date				
			self.date_end = self.promotion_end_date	
		
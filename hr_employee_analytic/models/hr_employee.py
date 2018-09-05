from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import api, fields, models, _

class hr_employee(models.Model):
	_inherit = "hr.employee"
	_order = "end_date desc " 

	@api.depends('contract_ids.date_end','contract_ids.employee_id','contract_ids.date_start','contract_ids.working_hours','contract_ids.type_id','end_date')
	@api.multi
	def get_detail_contract(self):
		for me_id in self :
			contract_id = me_id.contract_id

			if contract_id :
				me_id.working_hour = contract_id.working_hours
				me_id.type_id = contract_id.type_id.id
				me_id.start_date = contract_id.date_startW
				me_id.end_date = contract_id.date_end
				me_id.tgl_masuk = contract_id.date_start

			if me_id.end_date :
				d1=datetime.strptime(str(me_id.end_date),'%Y-%m-%d')
				d3=d1-datetime.today()
				me_id.days_left=str(d3.days)

 
	work_location_analytic = fields.Many2one('account.analytic.account','Work Location')
	working_hour = fields.Many2one('resource.calendar','Working Schedule', compute='get_detail_contract', store=True)
	type_id = fields.Many2one('hr.contract.type','Status Type', compute='get_detail_contract', store=True)
	end_date = fields.Date('Contract End Date', compute='get_detail_contract', store=True)
	start_date = fields.Date('Contract Start Date', compute='get_detail_contract', store=True)
	today=fields.Date(string="Date Diff",default=fields.Date.today)
	days_left = fields.Integer(string="Warning Date",compute='get_detail_contract')

	@api.onchange('work_location_analytic')  
	def check_change(self):
		if self.work_location_analytic:
			self.work_location = self.work_location_analytic.name

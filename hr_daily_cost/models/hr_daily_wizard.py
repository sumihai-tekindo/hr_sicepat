from openerp import models, fields, api

class HrDailyWizard(models.TransientModel):
	_name = 'hr.daily.wizard'

	employee_ids = fields.Many2many('hr.employee')
	date_from = fields.Date()
	date_to = fields.Date()

	@api.multi
	def query_data(self):
		self.ensure_one()
		all_nik = []
		for val in self.employee_ids:
			all_nik.append(str(val.nik))
		self.env['hr.daily.cost'].cron_job(self.date_from, self.date_to, all_nik)
		return {'type': 'ir.actions.act_window_close'}
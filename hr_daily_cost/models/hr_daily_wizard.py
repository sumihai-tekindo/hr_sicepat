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
		self.env['hr.daily.cost'].with_context({'date_from':self.date_from, 'date_to':self.date_to, 'all_nik':all_nik}).cron_job()
		return {'type': 'ir.actions.act_window_close'}
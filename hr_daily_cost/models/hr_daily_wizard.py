from openerp import models, fields, api

class HrDailyWizard(models.TransientModel):
	_name = 'hr.daily.wizard'

	date_from = fields.Date()
	date_to = fields.Date()

	@api.multi
	def query_data(self):
		self.ensure_one()
		self.env['hr.daily.cost'].cron_job(self.date_from,self.date_to)
		return {'type': 'ir.actions.act_window_close'}
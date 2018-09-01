from openerp import api, fields, models


class LeaveCategoryMaster(models.Model):
	_name = 'hr.category.master'

	leave_type    		  = fields.Many2one('hr.holidays.status', string='Leave Type', required=True)
	name                  = fields.Char(string="Description", required=True) 
	number_of_days 		  = fields.Float(string='Number Of Days', )
	leave_tag	  		  = fields.Many2many('hr.employee.category', string='Leave Tag')
	gender                = fields.Selection([
								('male', "Male"),
								('female', "Female"),
								('all', "All"),
							], default='all')
	job_ids       	      = fields.Many2many('hr.job', required=True)


class HrHolidays(models.Model):
	_inherit = "hr.holidays"

	@api.onchange('holiday_status_id', 'holiday_type')
	def _onchange_price(self):
		if self.holiday_status_id:
			val = self.env['hr.category.master'].search([('leave_type','=',self.holiday_status_id.id)])
			
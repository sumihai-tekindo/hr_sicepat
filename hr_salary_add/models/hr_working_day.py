from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

class hr_working_day(models.Model):
	_inherit = 'resource.calendar'

	working_days = fields.Integer(string="Total Working Days")

	@api.constrains('working_days')
	def _check_working_days(self):
		self.ensure_one()
		if self.working_days < 0:
			raise ValidationError(_("Fields Working Days must be positive Number"))
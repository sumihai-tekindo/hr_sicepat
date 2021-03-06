from openerp import models, fields, api

class HrSalaryRule(models.Model):
	_inherit = "hr.salary.rule"

	is_template = fields.Boolean()

	@api.multi
	def set_to_template(self):
		if self.is_template == False:
			self.is_template = True


class HrSalaryRule(models.Model):
	_inherit = "hr.payroll.structure"

	is_template = fields.Boolean()
	is_expense = fields.Boolean()

	@api.multi
	def set_to_template(self):
		if self.is_template == False:
			self.is_template = True
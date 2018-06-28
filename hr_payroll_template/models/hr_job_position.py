from openerp import models, fields, api

class HrJobTitle(models.Model):
	_inherit = "hr.job"

	job_code= fields.Char('Job Code')
	
	
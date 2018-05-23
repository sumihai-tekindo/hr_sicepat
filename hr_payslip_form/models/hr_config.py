from openerp import models, fields, api

class hr_config_setting(models.TransientModel):
	_inherit = 'hr.config.settings'

	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id)
	hr_payslip_phone = fields.Char(related='company_id.hr_payslip_phone')
	hr_payslip_email = fields.Char(related='company_id.hr_payslip_email')

class res_company(models.Model):
	_inherit = 'res.company'

	hr_payslip_phone = fields.Char()
	hr_payslip_email = fields.Char()
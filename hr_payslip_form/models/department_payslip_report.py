# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class department_payslip_report(models.TransientModel):
	_name = "department.payslip.report"

	# period_id = fields.Many2one("account.period","Period",required=True)
	start_date = fields.Date(string="Start Date",required=True)
	end_date = fields.Date(string="End Date",required=True)
	department_id = fields.Many2one("hr.department","Region/Dept.",required=True)

	@api.multi
	def print_report(self,):
		self.ensure_one()
		employee_ids = [x.id for x in self.env['hr.employee'].search([('department_id','=',self.department_id.id)])]
		payslip_ids = self.env['hr.payslip'].search([('employee_id','in',employee_ids),('date_from','>=',self.start_date),('date_to','>=',self.end_date),('state','!=','cancel')])
		datas = {
            'model': 'hr.payslip',
            'start_date': self.start_date or False,
            'end_date': self.end_date or False,
            'department_id': self.department_id.id or False,
			'ids': [x.id for x in payslip_ids],
			'department_name':self.department_id.name or 'Payslips',
			}
		return {
				'type': 'ir.actions.report.xml',
				'report_name': 'department.payslip.report.xls',
				'datas': datas
				}
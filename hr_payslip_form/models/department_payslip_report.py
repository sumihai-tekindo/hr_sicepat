# -*- coding: utf-8 -*-
from datetime import date
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, Warning

class department_payslip_report(models.TransientModel):
	_name = "department.payslip.report"

	start_date = fields.Date(string="Start Date",required=True,default=lambda *x: (date.today()+ relativedelta(months=-1)).strftime('%Y-%m-21'))
	end_date = fields.Date(string="End Date",required=True,default=lambda *x: date.today().strftime('%Y-%m-20'))
	report_model = fields.Selection(
		[('department','Per Employee in a Region'),
		('totalled','Totalled per Bank'),
		('all','Per Region in selected Region'),
		('functional','Per Job Position in selected Region')],
		"Report Type",required=True)
	department_ids = fields.Many2many("hr.department","payslip_report_department_rel","wiz_id","dept_id","Department(s)",
		help="Select Department(s) you want to print",required=True)

	@api.multi
	def print_report(self):
		self.ensure_one()
		employee_ids = [e.id for e in self.env['hr.employee'].search([('department_id', 'in', [d.id for d in self.department_ids]), '|', ('active','=',True), ('active','=',False)])]
		payslip_ids = self.env['hr.payslip'].search([('employee_id','in',employee_ids),('date_from','>=',self.start_date),('date_to','<=',self.end_date),('state','!=','cancel')])

		if not payslip_ids:
			raise Warning(_('No payslip records for the given date between %s and %s') % (self.start_date, self.end_date))
		
		datas = {
	            'model': 'hr.payslip',
	            'start_date': self.start_date or False,
	            'end_date': self.end_date or False,
	            'department_ids': [d.id for d in self.department_ids],
				'ids': [x.id for x in payslip_ids],
				't_report': self.report_model,
			}
		result = {
				'type': 'ir.actions.report.xml',
				'datas': datas
			}
		if self.report_model=='department':
			result.update({'report_name': 'department.payslip.report.xls'})
		elif self.report_model=='all':
			result.update({'report_name': 'all.payslip.report.xls'})
		elif self.report_model=='totalled':
			result.update({'report_name': 'totalled.payslip.report.xls'})
		else:
			result.update({'report_name': 'functional.payslip.report.xls'})
		
		return result
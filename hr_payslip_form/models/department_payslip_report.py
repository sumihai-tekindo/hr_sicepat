# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class department_payslip_report(models.TransientModel):
	_name = "department.payslip.report"

	# period_id = fields.Many2one("account.period","Period",required=True)
	start_date = fields.Date(string="Start Date",required=True,default=lambda x:'2016-09-21')
	end_date = fields.Date(string="End Date",required=True,default=lambda x:'2016-10-20')
	report_model = fields.Selection(
		[('department','Per Employee in a Region'),
		('totalled','Totalled per Bank'),
		('all','Per Region in selected Region'),
		('functional','Per Job Position in selected Region')],
		"Report Type",required=True)
	department_id = fields.Many2one("hr.department","Region/Dept.",required=False)
	department_ids = fields.Many2many("hr.department","payslip_report_department_rel","wiz_id","dept_id","Department(s)",
		help="Select Department(s) you want to print",default=lambda x:[315])

	@api.multi
	def print_report(self,):
		self.ensure_one()
		if self.report_model=='department':
			employee_ids = [x.id for x in self.env['hr.employee'].search([('department_id','=',self.department_id.id)])]
		elif self.report_model=='all':
			employee_ids = [x.id for x in self.env['hr.employee'].search([('department_id','in',[x.id for x in self.department_ids])])]
		else:
			employee_ids = [x.id for x in self.env['hr.employee'].search([('department_id','in',[x.id for x in self.department_ids])])]

		payslip_ids = self.env['hr.payslip'].search([('employee_id','in',employee_ids),('date_from','>=',self.start_date),('date_to','<=',self.end_date),('state','!=','cancel')])


		datas = {
            'model': 'hr.payslip',
            'start_date': self.start_date or False,
            'end_date': self.end_date or False,
            'department_id': self.department_id and self.department_id.id or False,
            'department_ids': self.department_ids and [x.id for x in self.department_ids] or False,
			'ids': [x.id for x in payslip_ids],
			'department_name':self.department_id and self.department_id.name or 'Payslips',
			't_report': self.report_model,
			}
		if self.report_model=='department':
			return {
					'type': 'ir.actions.report.xml',
					'report_name': 'department.payslip.report.xls',
					'datas': datas
					}
		elif self.report_model=='all':
			return {
					'type': 'ir.actions.report.xml',
					'report_name': 'all.payslip.report.xls',
					'datas': datas
					}
		elif self.report_model=='totalled':
			return {
					'type': 'ir.actions.report.xml',
					'report_name': 'totalled.payslip.report.xls',
					'datas': datas
					}
		else:
			return {
					'type': 'ir.actions.report.xml',
					'report_name': 'functional.payslip.report.xls',
					'datas': datas
					}
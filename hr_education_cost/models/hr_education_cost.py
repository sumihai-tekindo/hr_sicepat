from openerp import api, fields, models

class EducationCost(models.Model):
	_name = 'hr.education.cost'

	name = fields.Char(string="Number", readonly=True)
	employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
	jabatan_id = fields.Many2one('hr.job', string='Jabatan', compute='_get_employee', store=True, readonly=True)
	tanggal = fields.Date()
	amount = fields.Float(string='Amount')

	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].get("hr.education.cost")
		return super(EducationCost, self).create(vals)

	@api.depends('employee_id.job_id')
	def _get_employee(self):
		self.ensure_one()
		self.jabatan_id = self.employee_id.job_id.id

	def check_employee(self, cr, uid, employee_id):
		data_employee = self.search(cr,uid,[('employee_id','=',employee_id)],limit=1)
		if data_employee:
			employee = self.browse(cr,uid, data_employee)
			return employee.amount

class HREducationPayslip(models.Model):
	_inherit = 'hr.payslip'
	
	def get_inputs(self, cr, uid, contract_ids, date_from, date_to, context=None):
		res = super(HREducationPayslip, self).get_inputs(cr, uid, contract_ids, date_from, date_to, context=context)
		browse_contract = self.pool.get('hr.contract').browse(cr,uid,contract_ids)
		contracts = {}
		for x in browse_contract:
			contracts.update({x.id:x})
		
		for result in res:
			c = contracts.get(result.get('contract_id',False),False)
			amount = self.pool.get('hr.education.cost').check_employee(cr, uid, c.employee_id.id)
			if result.get('code') == 'EDUCATION':
				result['amount'] = amount

		return res
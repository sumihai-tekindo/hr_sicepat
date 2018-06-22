from openerp import api, fields, models
from datetime import datetime
import pymssql

class DailyCost(models.Model):
	_name = 'hr.daily.cost'

	nik = fields.Char('Nik')
	name = fields.Char('Name')
	employee_id2 = fields.Char('Employee Id')
	employee_id = fields.Many2one('hr.employee', string="Employee id")
	expense_id = fields.Many2one('expense.type.masterdata')
	expense_type = fields.Char('Expense Type')
	amount = fields.Float('Amount')
	voucher_code = fields.Char('Voucher Code')
	trx_date = fields.Date()

	@api.model
	def cron_job(self, search_date_from=False, search_date_to=False):
		conn = pymssql.connect(server='pickup-pc-sicepat.cchjcxaiivov.ap-southeast-1.rds.amazonaws.com',
								user='odoohrd', password='0d00hrD', port=1433, database='EPETTYCASH')
		cr_mssql = conn.cursor(as_dict=True)
		condition = "ee.IsDisbursed = 'Y' and cast(ee.TxDatetime as DATE) = dateadd(day,-1, cast(getdate() as date))"
		if search_date_from and search_date_to:
			condition = "ee.IsDisbursed = 'Y' and cast(ee.TxDatetime as DATE) >= '%s' and cast(ee.TxDatetime as DATE) <= '%s' " % (str(search_date_from), str(search_date_to))
		query = """
					SELECT em.EmployeeNo, em.Name, ee.EmployeeId, ee.ExpenseId, ee.Amount, ee.VoucherCode, ee.TxDatetime, ee.IsDisbursed
					FROM EPETTYCASH.dbo.EmployeeExpense ee WITH (NOLOCK)
					LEFT JOIN EPETTYCASH.dbo.PettyCashExpense p WITH (NOLOCK) on ee.VoucherCode = p.VoucherCode
					LEFT JOIN EPETTYCASH.dbo.MsEmployee em WITH (NOLOCK) on ee.EmployeeId = em.Id
					WHERE """ + condition

		cr_mssql.execute(query)
		records = cr_mssql.fetchall()
		emp_dict = {}
		all_employee = self.env['hr.employee'].search([])
		for e in all_employee:
			emp_dict.update({e.nik:{'name': e.name, 'employee_id': e.id}})

		for record in records:
			if record['EmployeeNo'] in emp_dict.keys():
				data = self.env['expense.type.masterdata'].search([('expense_id','=', record['ExpenseId'] )])
				val = self.env['hr.daily.cost'].search([('voucher_code','=',record['VoucherCode']), ('expense_id','=',data.id)])
				if val:
					val.unlink()
				self.create({'nik': record['EmployeeNo'],
							 'name': emp_dict.get(record['EmployeeNo']).get('name'), 
							 'employee_id2': record['EmployeeId'], 
							 'employee_id': emp_dict.get(record['EmployeeNo']).get('employee_id'), 
							 'expense_id': data and data.id or False,
							 'expense_type': data and data.code or False,
							 'amount': record['Amount'],
							 'voucher_code': record['VoucherCode'], 
							 'trx_date': record['TxDatetime']})

	@api.model					 
	def sum_amount_perType(self, employee_id, date_from, date_to):
		ids = self.env['hr.daily.cost'].search([('employee_id','=',employee_id.id),('trx_date','>=',date_from),('trx_date','<=',date_to)])
		data = {}
		for val in ids:
			key = val.expense_type
			if data.get(key):
				data[key] += val.amount
			else: 
				data[key] = val.amount
		return data

class MasterDataDailyCost(models.Model):
	_name = 'expense.type.masterdata'

	expense_id = fields.Integer()
	name = fields.Char(string='Nama Komponen Tambahan')		
	code = fields.Char(string="Code")


class HRPayslip(models.Model):
	_inherit = 'hr.payslip'
	
	def get_inputs(self, cr, uid, contract_ids, date_from, date_to, context=None):
		res = super(HRPayslip, self).get_inputs(cr, uid, contract_ids, date_from, date_to, context=context)

		browse_contract = self.pool.get('hr.contract').browse(cr,uid,contract_ids)
		contracts = {}
		for x in browse_contract:
			contracts.update({x.id:x})

		for result in res:
			c = contracts.get(result.get('contract_id',False),False)
			data = self.pool.get('hr.daily.cost').sum_amount_perType(cr, uid, c.employee_id, date_from, date_to)
			if result.get('code') in data.keys():
				result['amount'] = data[result.get('code')]
		return res
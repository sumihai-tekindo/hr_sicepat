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
	def cron_job(self, search_date_from=False, search_date_to=False, all_nik=False):
		conn = pymssql.connect(server='pickup-pc-sicepat.cchjcxaiivov.ap-southeast-1.rds.amazonaws.com',
								user='odoohrd', password='0d00hrD', port=1433, database='EPETTYCASH')
		cr_mssql = conn.cursor(as_dict=True)
		condition = "ee.IsDisbursed = 'Y' and cast(ee.TxDatetime as DATE) = dateadd(day,-1, cast(getdate() as date))"
		if search_date_from and search_date_to:
			condition = "cast(pe.TxDate as DATE) >= '%s' and cast(pe.TxDate as DATE) <= '%s' " % (str(search_date_from), str(search_date_to))
		elif search_date_from and search_date_to and all_nik:
			condition = "cast(pe.TxDate as DATE) >= '%s' and cast(pe.TxDate as DATE) <= '%s' and me.EmployeeNo in ("+all_nik+")" % (str(search_date_from), str(search_date_to))
		query = """
					SELECT me.EmployeeNo, me.Name, pe.EmployeeId, pe.VoucherCode, ee.IsDisbursed,
					COALESCE(pe.ExpenseId, ee.ExpenseId) as ExpenseId, 
					CASE
						WHEN pe.VoucherCode IS NULL
						THEN pe.Amount
						ELSE ee.Amount
					END AS Amount,
					CASE
						WHEN pe.VoucherCode IS NULL
						THEN pe.TxDate
						ELSE ee.TxDatetime
					END AS NewTxDate

					FROM EPETTYCASH.dbo.PettyCashExpense pe WITH (NOLOCK)
					LEFT JOIN EPETTYCASH.dbo.EmployeeExpense ee WITH (NOLOCK) ON pe.VoucherCode = ee.VoucherCode AND ee.IsDisbursed = 'Y'
					LEFT JOIN EPETTYCASH.dbo.MsEmployee me WITH (NOLOCK) ON COALESCE(pe.EmployeeId, ee.EmployeeId) = me.Id
					WHERE """ + condition

		cr_mssql.execute(query)
		records = cr_mssql.fetchall()
		# print '================',record
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
							 'trx_date': record['NewTxDate']})

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
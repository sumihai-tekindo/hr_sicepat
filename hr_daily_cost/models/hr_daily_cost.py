from openerp import api, fields, models
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
import pymssql

class DailyCost(models.Model):
	_name = 'hr.daily.cost'

	nik = fields.Char('Nik')
	name = fields.Char('Name')
	employee_id2 = fields.Char('Employee Id')
	employee_id = fields.Many2one('hr.employee', string="Employee")
	expense_id = fields.Many2one('expense.type.masterdata')
	expense_type = fields.Char('Expense Type')
	amount = fields.Float('Amount')
	voucher_code = fields.Boolean()
	trx_date = fields.Date()

	@api.model	
	def cron_job(self):
		all_nik = self._context.get('all_nik')
		if not self._context.get('date_from') and not self._context.get('date_to'):
			search_date_from = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
			search_date_to = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
		else:
			search_date_from = self._context.get('date_from')
			search_date_to = self._context.get('date_to')
		
		get_credential = self.env['ir.config_parameter'].search([('key','in',['pettycash.host', 'pettycash.user', 'pettycash.password', 'pettycash.port', 'pettycash.db'])])
		get_config = {
			'user'		: '',
			'password'	: '',
			'host'		: '',
			'database'	: '',
			'port'		: '',
		}
		if get_credential:
			for val in get_credential:
				if val.key == 'pettycash.host':
					get_config.update({'host': val.value})
				elif val.key == 'pettycash.user':
					get_config.update({'user': val.value})
				elif val.key == 'pettycash.password':
					get_config.update({'password': val.value})
				elif val.key == 'pettycash.port':
					get_config.update({'port': val.value})
				elif val.key == 'pettycash.db':
					get_config.update({'database': val.value})

		conn = pymssql.connect(server=get_config['host'], user=get_config['user'], password=get_config['password'], 
			port=get_config['port'], database=get_config['database'])
		cr_mssql = conn.cursor(as_dict=True)

		if all_nik:
			condition = "cast(pe.TxDate as DATE) >= '%s' and cast(pe.TxDate as DATE) <= '%s' and me.EmployeeNo in ('%s')" %(str(search_date_from), str(search_date_to), "','".join(all_nik) )
		else:
			condition = "cast(pe.TxDate as DATE) >= '%s' and cast(pe.TxDate as DATE) <= '%s' " % (str(search_date_from), str(search_date_to))
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
					LEFT JOIN EPETTYCASH.dbo.EmployeeExpense ee WITH (NOLOCK) ON pe.VoucherCode = ee.VoucherCode
					LEFT JOIN EPETTYCASH.dbo.MsEmployee me WITH (NOLOCK) ON COALESCE(pe.EmployeeId, ee.EmployeeId) = me.Id
					WHERE ee.IsDisbursed = 'Y' AND """ + condition

		cr_mssql.execute(query)
		records = cr_mssql.fetchall()
		emp_dict = {}
		all_employee = self.env['hr.employee'].search([])
		for e in all_employee:
			emp_dict.update({e.nik:{'name': e.name, 'employee_id': e.id}})

		masterdata_dict = {}
		expense_type_masterdata = self.env['expense.type.masterdata'].search([])
		for val in expense_type_masterdata:
			masterdata_dict.update({val.expense_id:{'id':val.id, 'code':val.code}})

		for record in records:
			if record['EmployeeNo'] in emp_dict.keys():
				domain = [ 
						('voucher_code','=',bool(record['VoucherCode'])),
						('expense_id','=',masterdata_dict.get(record['ExpenseId']).get('id')),
						('trx_date','=',record['NewTxDate'][:10]), 
						('employee_id','=',emp_dict.get(record['EmployeeNo']).get('employee_id'))]

				if record['VoucherCode']:
					domain.append(('name','=',record['VoucherCode']))
				
				data_from_hr_daily_cost = self.env['hr.daily.cost'].search(domain)
				if not data_from_hr_daily_cost:
					date_ctx = record['NewTxDate'][:10]
					rr=self.create({'nik': record['EmployeeNo'],
								 'name': record['VoucherCode'] or self.env['ir.sequence'].with_context(ir_sequence_date=date_ctx).get('daily.cost'), 
								 'employee_id2': record['EmployeeId'], 
								 'employee_id': emp_dict.get(record['EmployeeNo']).get('employee_id'), 
								 'expense_id': masterdata_dict.get(record['ExpenseId']).get('id') or False,
								 'expense_type': masterdata_dict.get(record['ExpenseId']).get('code') or False,
								 'amount': record['Amount'],
								 'voucher_code': bool(record['VoucherCode']),
								 'trx_date': record['NewTxDate'][:10]})



	# def cron_job2(self):
	# 	all_nik = self._context.get('all_nik')
	# 	if not self._context.get('date_from') and not self._context.get('date_to'):
	# 		search_date_from = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
	# 		search_date_to = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
	# 	else:
	# 		search_date_from = self._context.get('date_from')
	# 		search_date_to = self._context.get('date_to')
		
	# 	get_credential = self.env['ir.config_parameter'].search([('key','in',['pettycash.host', 'pettycash.user', 'pettycash.password', 'pettycash.port', 'pettycash.db'])])
	# 	get_config = {
	# 		'user'		: '',
	# 		'password'	: '',
	# 		'host'		: '',
	# 		'database'	: '',
	# 		'port'		: '',
	# 	}
	# 	if get_credential:
	# 		for val in get_credential:
	# 			if val.key == 'pettycash.host':
	# 				get_config.update({'host': val.value})
	# 			elif val.key == 'pettycash.user':
	# 				get_config.update({'user': val.value})
	# 			elif val.key == 'pettycash.password':
	# 				get_config.update({'password': val.value})
	# 			elif val.key == 'pettycash.port':
	# 				get_config.update({'port': val.value})
	# 			elif val.key == 'pettycash.db':
	# 				get_config.update({'database': val.value})

	# 	conn = pymssql.connect(server=get_config['host'], user=get_config['user'], password=get_config['password'], 
	# 		port=get_config['port'], database=get_config['database'])
	# 	cr_mssql = conn.cursor(as_dict=True)

	# 	if all_nik:
	# 		condition = "cast(pe.TxDate as DATE) >= '%s' and cast(pe.TxDate as DATE) <= '%s' and me.EmployeeNo in ('%s')" %(str(search_date_from), str(search_date_to), "','".join(all_nik) )
	# 	else:
	# 		condition = "cast(pe.TxDate as DATE) >= '%s' and cast(pe.TxDate as DATE) <= '%s' " % (str(search_date_from), str(search_date_to))
	# 	query = """
	# 				SELECT me.EmployeeNo, me.Name, pe.EmployeeId, pe.VoucherCode, ee.IsDisbursed,
	# 				COALESCE(pe.ExpenseId, ee.ExpenseId) as ExpenseId, 
	# 				CASE
	# 					WHEN pe.VoucherCode IS NULL
	# 					THEN pe.Amount
	# 					ELSE ee.Amount
	# 				END AS Amount,
	# 				CASE
	# 					WHEN pe.VoucherCode IS NULL
	# 					THEN pe.TxDate
	# 					ELSE ee.TxDatetime
	# 				END AS NewTxDate

	# 				FROM EPETTYCASH.dbo.PettyCashExpense pe WITH (NOLOCK)
	# 				LEFT JOIN EPETTYCASH.dbo.EmployeeExpense ee WITH (NOLOCK) ON pe.VoucherCode = ee.VoucherCode
	# 				LEFT JOIN EPETTYCASH.dbo.MsEmployee me WITH (NOLOCK) ON COALESCE(pe.EmployeeId, ee.EmployeeId) = me.Id
	# 				WHERE ee.IsDisbursed = 'Y' AND """ + condition

	# 	cr_mssql.execute(query)
	# 	records = cr_mssql.fetchall()
	# 	emp_dict = {}
	# 	all_employee = self.env['hr.employee'].search([])
	# 	for e in all_employee:
	# 		emp_dict.update({e.nik:{'name': e.name, 'employee_id': e.id}})

	# 	masterdata_dict = {}
	# 	expense_type_masterdata = self.env['expense.type.masterdata'].search([])
	# 	for val in expense_type_masterdata:
	# 		masterdata_dict.update({val.expense_id:{'id':val.id, 'code':val.code}})

	# 	list_voucher = []
	# 	for record in records:
	# 		list_voucher.append(record['VoucherCode'])
			
	# 	domain = [('name', 'in', list_voucher)]	
	# 	data_from_hr_daily_cost = self.env['hr.daily.cost'].search(domain)
	# 	all_voucher = [x.name for x in data_from_hr_daily_cost if x]

	# 	for record in records:
	# 		if record['VoucherCode'] not in all_voucher:
	# 			date_ctx = record['NewTxDate'][:10]
	# 			rr=self.create({'nik': record['EmployeeNo'],
	# 						 'name': record['VoucherCode'] or self.env['ir.sequence'].with_context(ir_sequence_date=date_ctx).get('daily.cost'), 
	# 						 'employee_id2': record['EmployeeId'], 
	# 						 'employee_id': emp_dict.get(record['EmployeeNo']).get('employee_id'), 
	# 						 'expense_id': masterdata_dict.get(record['ExpenseId']).get('id') or False,
	# 						 'expense_type': masterdata_dict.get(record['ExpenseId']).get('code') or False,
	# 						 'amount': record['Amount'],
	# 						 'voucher_code': bool(record['VoucherCode']),
	# 						 'trx_date': record['NewTxDate'][:10]})



	@api.model					 
	def sum_amount_perType(self, employee_id, date_from, date_to, working_hours_id):
		ids = self.env['hr.daily.cost'].search([('employee_id','=',employee_id.id),('trx_date','>=',date_from),('trx_date','<=',date_to)])

		data = {}
		for val in ids:
			key = val.expense_type
			trx_date = datetime.strptime(val.trx_date, '%Y-%m-%d')
			is_holiday = self.env['hr.holidays.public'].is_public_holiday(trx_date, employee_id=employee_id.id)
			working_hours_on_day = self.env['resource.calendar'].working_hours_on_day(working_hours_id, trx_date)

			if data.get(key) and working_hours_on_day and not is_holiday:
				data[key] += val.amount
			else: 
				data[key] = val.amount

		return data

class MasterDataDailyCost(models.Model):
	_name = 'expense.type.masterdata'

	expense_id = fields.Integer()
	name = fields.Char(string='Nama Komponen Tambahan')		
	code = fields.Char(string="Code")

	@api.multi
	def name_get(self):
		result = []
		for rec in self:
			name_get = rec.name
			if self._context.get('show_code'):
				name_get = rec.code
			result.append((rec.id, "%s" % (name_get)))
		return result

	@api.model
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		recs = self.browse()
		if name:
			recs = self.search([('code', '=', name)] + args, limit=limit)
		if not recs:
			recs = self.search([('name', operator, name)] + args, limit=limit)
		return recs.name_get()


class HRPayslip(models.Model):
	_inherit = 'hr.payslip'
	
	def get_inputs(self, cr, uid, contract_ids, date_from, date_to, context=None):
		res = super(HRPayslip, self).get_inputs(cr, uid, contract_ids, date_from, date_to, context=context)

		browse_contract = self.pool.get('hr.contract').browse(cr,uid,contract_ids)
		working_hours_id = browse_contract.working_hours
		
		contracts = {}
		for x in browse_contract:
			contracts.update({x.id:x})

		for result in res:
			c = contracts.get(result.get('contract_id',False),False)
			data = self.pool.get('hr.daily.cost').sum_amount_perType(cr, uid, c.employee_id, date_from, date_to, working_hours_id)
			if result.get('code') in data.keys():
				result['amount'] = data[result.get('code')]
		return res
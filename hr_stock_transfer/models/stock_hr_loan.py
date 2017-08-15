from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID, api

class stock_quant(osv.osv):
	_inherit = "stock.quant"

	_columns = {
			'employee_id': fields.many2one('hr.employee', 'Employee'),
			'is_loan': fields.boolean('Employee Loan'),
			'loan_id': fields.many2one('hr.loan', 'Loan #'),
		}

	def _prepare_account_move_line(self, cr, uid, move, qty, cost, credit_account_id, debit_account_id, context=None):
		"""
		Generate the account.move.line values to post to track the stock valuation difference due to the
		processing of the given quant.
		"""
		if context is None:
			context = {}
		loan_pool = self.pool.get('hr.loan')
		stock_loan_obj = self.pool.get('stock.hr.loan')
		res = super(stock_quant, self)._prepare_account_move_line(cr, uid, move, qty, cost, credit_account_id, debit_account_id, context=context)
		account_analytic_id = context.get('account_analytic_id', False)
		account_analytic_dest_id = context.get('account_analytic_dest_id', False)

		if res and account_analytic_id and account_analytic_dest_id:
			res[0][2]['analytic_account_id'] = account_analytic_dest_id
			res[1][2]['analytic_account_id'] = account_analytic_id

		is_loan = context.get('is_loan') and context['is_loan'] or False
		loan = context.get('loan') and context['loan'] or False
		employee_id = context.get('employee_id', False)
		quant_id = context.get('quant_id', False)
		if res and employee_id and is_loan and (not loan or (loan and loan.state != 'reject')): 
			stock_id = stock_loan_obj.search(cr, SUPERUSER_ID, [], limit=1)
			stock = stock_loan_obj.browse(cr, SUPERUSER_ID, stock_id)[0]
			current_date = date.today()
			next_month = (current_date + relativedelta(months=1)).strftime('%Y-%m-20')
			date_install = int(current_date.strftime('%d'))>=20 and next_month or current_date.strftime('%Y-%m-20')
			employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)
			loan_type = employee and employee.company_id and employee.company_id.piutang_hp_loan_type_id and employee.company_id.piutang_hp_loan_type_id.id or False
			if loan:
				raise osv.except_osv(_('Error!'),_("There is an existing loan for employee %s. You should remove that loan by rejecting or deleting the loan if it is possible." % (employee.name)))
			else:
				loan_val = {
						'employee_id': employee_id,
						'original': cost,
						'nilai_pinjaman': stock.rate_silent,
						'tanggal': move.date or False,
						'tenor_angsuran': 1, 
						'tanggal_awal_angsuran': date_install,
						'payment_method': 'other', 
						'loan_type': loan_type,
					}
				loan_id = loan_pool.create(cr, SUPERUSER_ID, loan_val, context=context)
				self.pool.get('stock.quant').write(cr, SUPERUSER_ID, quant_id, {'loan_id': loan_id})
				new_move_line=list()
				for a, b, move_line in res:
					if move_line['debit'] > 0.0:
						move_line['debit'] = stock.rate_silent
		
					if move_line['credit'] > 0:
						new_line = move_line.copy()
						new_line['credit'] = stock.rate_silent - move_line['credit']
						new_line['account_id'] = stock.account_id.id
						new_move_line.append((0, 0, new_line))
					new_move_line.append((0, 0, move_line))
				res = new_move_line

		return res

	def _create_account_move_line(self, cr, uid, quants, move, credit_account_id, debit_account_id, journal_id, context=None):
		#group quants by cost
		quant_cost_qty = {}
		quant_analytic = {}
		for quant in quants:
			if quant_cost_qty.get(quant.cost):
				quant_cost_qty[quant.cost] += quant.qty
			else:
				quant_cost_qty[quant.cost] = quant.qty
			quant_analytic[quant.cost] = {
					'account_analytic_id': quant.account_analytic_id and quant.account_analytic_id.id or False,
					'account_analytic_dest_id': quant.account_analytic_dest_id and quant.account_analytic_dest_id.id or False,
					'employee_id': quant.employee_id and quant.employee_id.id or False,
					'is_loan': quant.is_loan,
					'loan': quant.loan_id or False,
					'quant_id': quant.id,
				}
		move_obj = self.pool.get('account.move')
		for cost, qty in quant_cost_qty.items():
			if quant_analytic.get(cost):
				context.update({
						'account_analytic_id': quant_analytic[cost].get('account_analytic_id', False),
						'account_analytic_dest_id': quant_analytic[cost].get('account_analytic_dest_id', False),
						'employee_id': quant_analytic[cost].get('employee_id', False),
						'is_loan': quant_analytic[cost].get('is_loan'),
						'loan': quant_analytic[cost].get('loan', False),
						'quant_id': quant_analytic[cost].get('quant_id', False),
					})
			move_lines = self._prepare_account_move_line(cr, uid, move, qty, cost, credit_account_id, debit_account_id, context=context)
			period_id = context.get('force_period', self.pool.get('account.period').find(cr, uid, context=context)[0])
			move_obj.create(cr, uid, {'journal_id': journal_id,
									  'line_id': move_lines,
									  'period_id': period_id,
									  'date': fields.date.context_today(self, cr, uid, context=context),
									  'ref': move.picking_id.name}, context=context)

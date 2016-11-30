import openerp
from openerp import tools
from openerp.osv import fields, osv, expression

from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _

from openerp import SUPERUSER_ID, api


class stock_quant(osv.osv):
	_inherit = "stock.quant"

	_columns = {
		"employee_id": fields.many2one("hr.employee","Employee"),
		'loan_id': fields.many2one("hr.loan",'Employee Loan'),
		}

	def _prepare_account_move_line(self, cr, uid, move, qty, cost, credit_account_id, debit_account_id, context=None):
		"""
		Generate the account.move.line values to post to track the stock valuation difference due to the
		processing of the given quant.
		"""
		res = super(stock_quant,self)._prepare_account_move_line(cr, uid, move, qty, cost, credit_account_id, debit_account_id, context=context)
		account_analytic_id = context.get('account_analytic_id',False)
		account_analytic_dest_id = context.get('account_analytic_dest_id',False)
		if res and account_analytic_id and account_analytic_dest_id:
			res[0][2]['analytic_account_id']=account_analytic_dest_id
			res[1][2]['analytic_account_id']=account_analytic_id


		loan_pool = self.pool.get('hr.loan')
		is_loan_id = context.get('loan_id',False) and context.get('loan_id').id or False
		loan_state = context.get('loan_id',False) and context.get('loan_id').state or False
		employee_id = context.get('employee_id',False)
		quant_id = context.get('quant_id',False)
		if res and context.get('employee_id',False) and (not is_loan_id or (is_loan_id and loan_state not in ('reject'))): 
			current_date = date.today()
			next_month = (current_date+relativedelta(months=1)).strftime('%Y-%m-20')
			date_install = int(current_date.strftime('%d'))>=20 and next_month or current_date.strftime('%Y-%m-20')
			if context is None:
				context = {}
			loan_val = {
				'employee_id'			: employee_id or False,
				'nilai_pinjaman'		: cost,
				'tanggal'				: move.date or False,
				'tenor_angsuran'		: 1, 
				'tanggal_awal_angsuran'	: date_install,
				'payment_method'		: 'other', 
				}
			if loan_state:
				raise osv.except_osv(_('Error!'),_("There is an existing loan in  for employee %s. You should remove that loan by rejecting or deleting the loan if it is possible."%(operation.product_id.name,operation.employee_id.name)))
			else:
				loan_id = loan_pool.create(cr,uid,loan_val,context=context)
				self.pool.get('stock.quant').write(cr,SUPERUSER_ID,quant_id,{'loan_id':loan_id})
				
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
											'account_analytic_id':quant.account_analytic_id and quant.account_analytic_id.id or False,
											'account_analytic_dest_id':quant.account_analytic_dest_id and quant.account_analytic_dest_id.id or False,
											'employee_id': quant.employee_id and quant.employee_id.id or False,
											'loan_id': quant.loan_id or False,
											'quant_id': quant.id or False,
										}
		move_obj = self.pool.get('account.move')
		for cost, qty in quant_cost_qty.items():
			if quant_analytic.get(cost,False):
				context.update({
					'account_analytic_id':quant_analytic.get(cost,False) and quant_analytic.get(cost).get('account_analytic_id',False),
					'account_analytic_dest_id':quant_analytic.get(cost,False) and quant_analytic.get(cost).get('account_analytic_dest_id',False),
					'employee_id':quant_analytic.get(cost,False) and quant_analytic.get(cost).get('employee_id',False),
					'loan_id':quant_analytic.get(cost,False) and quant_analytic.get(cost).get('loan_id',False),
					'quant_id':quant_analytic.get(cost,False) and quant_analytic.get(cost).get('quant_id',False),
					})
			move_lines = self._prepare_account_move_line(cr, uid, move, qty, cost, credit_account_id, debit_account_id, context=context)
			period_id = context.get('force_period', self.pool.get('account.period').find(cr, uid, context=context)[0])

			move_obj.create(cr, uid, {'journal_id': journal_id,
									  'line_id': move_lines,
									  'period_id': period_id,
									  'date': fields.date.context_today(self, cr, uid, context=context),
									  'ref': move.picking_id.name}, context=context)

from openerp.osv import fields, osv
import time
from openerp.tools import float_compare, float_is_zero
from openerp.tools.translate import _

class hr_payslip_confirm(osv.osv_memory):
	"""
	This wizard will confirm the all the selected draft invoices
	"""

	_name = "hr.payslip.confirm"
	_description = "Confirm the selected Payslips"

	def payslip_confirm(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		active_ids = context.get('active_ids', []) or []

		proxy = self.pool['hr.payslip']
		for record in proxy.browse(cr, uid, active_ids, context=context):
			if record.state not in ('draft'):
				raise osv.except_osv(_('Warning!'), _("Selected payslip(s) for employee %s (%s) cannot be confirmed as they are not in 'Draft' state."%(record.employee_id.name,record.name)))
		ret = self.pool.get('hr.payslip').process_sheet(cr,uid,active_ids,context={'grouped_slip':True})
		
		return {'type': 'ir.actions.act_window_close'}


class hr_payslip(osv.osv):
	_inherit = "hr.payslip"

	def inv_line_characteristic_hashcode(self, move_line):
		"""Overridable hashcode generation for invoice lines. Lines having the same hashcode
		will be grouped together if the journal has the 'group line' option. Of course a module
		can add fields to invoice lines that would need to be tested too before merging lines
		or not."""
		return "%s-%s-%s" % (
			move_line['account_id'],
			move_line.get('analytic_account_id', 'False'),
			move_line.get('tax_code_id', 'False'),
		)

	def group_move_lines(self, line):
		"""Merge account move lines (and hence analytic lines) if invoice line hashcodes are equals"""
		
		line2 = {}
		for l in line:
			tmp = self.inv_line_characteristic_hashcode(l)
			if tmp in line2:
				am = line2[tmp]['debit'] - line2[tmp]['credit'] + (l['debit'] - l['credit'])
				line2[tmp]['debit'] = (am > 0) and am or 0.0
				line2[tmp]['credit'] = (am < 0) and -am or 0.0
				line2[tmp]['tax_amount'] += l['tax_amount']
				# line2[tmp]['analytic_lines'] += l['analytic_lines']
			else:
				line2[tmp] = l
		# print "----------------->",line2
		line = []
		for key, val in line2.items():
			line.append((0,0,val))
		return line

	def _generate_grouped_slip(self, cr, uid, ids,move, context=None):
		move_pool = self.pool.get('account.move')
		period_pool = self.pool.get('account.period')
		precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Payroll')
		timenow = time.strftime('%Y-%m-%d')

		line_ids = []
		debit_sum = 0.0
		credit_sum = 0.0

		for slip in self.browse(cr,uid,ids,context=context):
			dept_name = slip.employee_id and slip.employee_id.department_id and slip.employee_id.department_id.name or ''
			job_name = slip.employee_id and slip.employee_id.job_id and slip.employee_id.job_id.name or ''
			if not slip.period_id:
				search_periods = period_pool.find(cr, uid, slip.date_to, context=context)
				period_id = search_periods[0]
			else:
				period_id = slip.period_id.id
			for line in slip.details_by_salary_rule_category:
				amt = slip.credit_note and -line.total or line.total
				if float_is_zero(amt, precision_digits=precision):
					continue
				#partner_id = line.salary_rule_id.register_id.partner_id and line.salary_rule_id.register_id.partner_id.id or default_partner_id
				debit_account_id = line.salary_rule_id.account_debit.id
				credit_account_id = line.salary_rule_id.account_credit.id

				if debit_account_id:

					debit_line = (0, 0, {
					'name': line.name,
					'date': timenow,
					#'partner_id': (line.salary_rule_id.register_id.partner_id or line.salary_rule_id.account_debit.type in ('receivable', 'payable')) and partner_id or False,
					'account_id': debit_account_id,
					'journal_id': slip.journal_id.id,
					'period_id': period_id,
					'debit': amt > 0.0 and amt or 0.0,
					'credit': amt < 0.0 and -amt or 0.0,
					'analytic_account_id': line.salary_rule_id.analytic_account_id and line.salary_rule_id.analytic_account_id.id or False,
					'tax_code_id': line.salary_rule_id.account_tax_id and line.salary_rule_id.account_tax_id.id or False,
					'tax_amount': line.salary_rule_id.account_tax_id and amt or 0.0,
				})
					line_ids.append(debit_line)
					debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

				if credit_account_id:

					credit_line = (0, 0, {
					'name': line.salary_rule_id.account_credit.name+' '+dept_name,
					'date': timenow,
					#'partner_id': (line.salary_rule_id.register_id.partner_id or line.salary_rule_id.account_credit.type in ('receivable', 'payable')) and partner_id or False,
					'account_id': credit_account_id,
					'journal_id': slip.journal_id.id,
					'period_id': period_id,
					'debit': amt < 0.0 and -amt or 0.0,
					'credit': amt > 0.0 and amt or 0.0,
					# 'analytic_account_id': line.salary_rule_id.analytic_account_id and line.salary_rule_id.analytic_account_id.id or False,
					'tax_code_id': line.salary_rule_id.account_tax_id and line.salary_rule_id.account_tax_id.id or False,
					'tax_amount': line.salary_rule_id.account_tax_id and amt or 0.0,
				})
					line_ids.append(credit_line)
					credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']

			if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
				acc_id = slip.journal_id.default_credit_account_id.id
				if not acc_id:
					raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Credit Account!')%(slip.journal_id.name))
				adjust_credit = (0, 0, {
					'name': _('Adjustment Entry'),
					'date': timenow,
					'partner_id': False,
					'account_id': acc_id,
					'journal_id': slip.journal_id.id,
					'period_id': period_id,
					'debit': 0.0,
					'credit': debit_sum - credit_sum,
				})
				line_ids.append(adjust_credit)

			elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
				acc_id = slip.journal_id.default_debit_account_id.id
				if not acc_id:
					raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(slip.journal_id.name))
				adjust_debit = (0, 0, {
					'name': _('Adjustment Entry'),
					'date': timenow,
					'partner_id': False,
					'account_id': acc_id,
					'journal_id': slip.journal_id.id,
					'period_id': period_id,
					'debit': credit_sum - debit_sum,
					'credit': 0.0,
				})
				line_ids.append(adjust_debit)

			
		return line_ids

	def _compute_grouped_slip(self, cr, uid, ids, context=None):
		period_pool = self.pool.get('account.period')
		move_pool = self.pool.get('account.move')
		mvl = {} # mvl = {dept_id:{job_id:[slip_ids]}}
		oslip = []
		for slip in self.browse(cr, uid, ids, context=context):
			current_dept = slip.employee_id and slip.employee_id.department_id and slip.employee_id.department_id.id or 'Undefined'
			current_job = slip.employee_id and slip.employee_id.job_id and slip.employee_id.job_id.id or 'Undefined'
			current_mvl_dept = mvl.get(current_dept,{})
			# print "----------->",mvl,current_dept
			oslip = mvl.get(current_dept,False) and mvl.get(current_dept).get(current_job,[]) or []
			oslip.append(slip.id)
			current_mvl_dept.update({current_job:oslip})
			mvl.update({current_dept:current_mvl_dept})
		slip_dict = []
		
		
		firstslip = self.browse(cr,uid,ids[0],context=context)
		if not firstslip.period_id:
			search_periods = period_pool.find(cr, uid, firstslip.date_to, context=context)
			period_id = search_periods[0]
		else:
			period_id = firstslip.period_id.id
		name = _('Payslip %s') % firstslip.payslip_run_id and firstslip.payslip_run_id.name or ''
		timenow = time.strftime('%Y-%m-%d')
		move = {
			'narration': name,
			'date': timenow,
			'ref': firstslip.number,
			'journal_id': firstslip.journal_id.id ,
			'period_id': period_id,
		}
		line_id = []
		
		for dept in mvl:
			for job in mvl.get(dept):
				slip_ids = mvl.get(dept).get(job)
				line=self._generate_grouped_slip(cr,uid,slip_ids,move,context=context)
				if line:
					for l in line:
						line_id.append(l[2])
		

		group_lines = self.group_move_lines(line_id)
		move.update({'line_id':group_lines})
		move_id = move_pool.create(cr, uid, move, context=context)
		self.write(cr, uid, [slip.id], {'move_id': move_id, 'period_id' : period_id}, context=context)
		if slip.journal_id.entry_posted:
			move_pool.post(cr, uid, [move_id], context=context)
			
		return True

	def process_sheet(self,cr,uid,ids,context=None):
		if not context:
			context= {}
		if context.get('grouped_slip',False):
			# print "idsssssssssssss=======>",ids
			slips = self.pool.get('hr.payslip')._compute_grouped_slip(cr,uid,ids,context=context)
			self.pool.get('hr.payslip').signal_workflow(cr, uid, [id_copy], 'hr_verify_sheet')
			return False
		return super(hr_payslip,self).process_sheet(cr,uid,ids,context=context)
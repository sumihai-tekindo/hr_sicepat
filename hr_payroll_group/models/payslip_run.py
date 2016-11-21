from datetime import date
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from openerp.osv import fields, osv
from openerp.exceptions import Warning as UserError

class hr_payslip_run_wizard(osv.osv_memory):
	_name = "hr.payslip.run.wizard"
	_columns = {
		"name": fields.char("Default Name",required=True),
		"date_start": fields.date("Start Date",required=True),
		"date_end"	: fields.date("End Date",required=True),
		"journal_id": fields.many2one("account.journal","Salary Journal",required=True),
		'credit_note': fields.boolean('Credit Note', help="If its checked, indicates that all payslips generated from here are refund payslips."),
		"department_ids" : fields.many2many("hr.department","hr_payslip_run_department_rel","run_id","dept_id","Departments"),

	}
	_defaults = {
		"name"			: lambda *x:'Payslip',
		"date_start"	: lambda *x: (date.today()+ relativedelta(months=-1)).strftime('%Y-%m-21'),
		"date_end"		: lambda *x: date.today().strftime('%Y-%m-20'),
		#"department_ids": lambda self,cr,uid,context: self.pool.get('hr.department').search(cr,uid,[])
		"department_ids": lambda *x:[315]
	}

	def generate_payslip_run(self,cr,uid,ids,context=None):
		if not context:
			context={}
		slip_pool = self.pool.get('hr.payslip')
		for wiz in self.browse(cr,uid,ids,context=context):
			curr_start = dt.strptime(wiz.date_start,'%Y-%m-%d').strftime('%b %Y')
			curr_end = dt.strptime(wiz.date_end,'%Y-%m-%d').strftime('%b %Y')
			from_date = wiz.date_start
			to_date  = wiz.date_end
			credit_note = wiz.credit_note
			slip_ids = []
			journal_id = wiz.journal_id and wiz.journal_id.id or False
			for dept in wiz.department_ids:
				value = {
					"name": wiz.name + ' %s - %s'%(curr_start,curr_end), 
					"date_start": wiz.date_start,
					"date_end": wiz.date_end,
					"department_id": dept and dept.id,
					'credit_note':wiz.credit_note,
					"journal_id": journal_id,
					}
				run_id = self.pool.get("hr.payslip.run").create(cr,uid,value,context=context)
				employee_ids = self.pool.get('hr.employee').search(cr,uid,[('department_id','=',dept.id)])
				for emp in self.pool.get('hr.employee').browse(cr, uid, employee_ids, context=context):
					slip_data = slip_pool.onchange_employee_id(cr, uid, [], from_date, to_date, emp.id, contract_id=False, context=context)
					res = {
						'employee_id': emp.id,
						'name': slip_data['value'].get('name', False),
						'struct_id': slip_data['value'].get('struct_id', False),
						'contract_id': slip_data['value'].get('contract_id', False),
						'payslip_run_id': run_id,
						'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids', False)],
						'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids', False)],
						'date_from': from_date,
						'date_to': to_date,
						'credit_note': credit_note,
						"journal_id" : slip_data['value'].get('journal_id',journal_id),
					}
					slip_ids.append(slip_pool.create(cr, uid, res, context=context))
			slip_pool.compute_sheet(cr, uid, slip_ids, context=context)
		return {'type': 'ir.actions.act_window_close'}

class hr_payslip_run(osv.osv):
	_inherit = "hr.payslip.run"

	_columns = {
		"department_id": fields.many2one("hr.department","Department",required=True)
	}
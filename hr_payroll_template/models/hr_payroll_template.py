from openerp import models, fields, api
import openerp.addons.decimal_precision as dp

class HrPayrollTemp(models.Model):
	_name = 'hr.payroll.template'
	
	name = fields.Char(required=True)
	code = fields.Char(required=True)
	sequence = fields.Integer(required=True, index=True, default=5)
	quantity = fields.Char()
	category_id = fields.Many2one('hr.salary.rule.category', string='Category', required=True)
	active = fields.Boolean(default=True)
	appears_on_payslip = fields.Boolean(string='Appears on Payslip', default=True)
	parent_rule_id = fields.Many2one('hr.salary.rule', string='Parent Salary Rule', index=True)
	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get())
	condition_select = fields.Selection([
		('none', 'Always True'),
		('range', 'Range'),
		('python', 'Python Expression')
	], string="Condition Based on", default='none', required=True)
	condition_range = fields.Char(string='Range Based on', default='contract.wage',
		help='This will be used to compute the % fields values; in general it is on basic, '
			 'but you can also use categories code fields in lowercase as a variable names '
			 '(hra, ma, lta, etc.) and the variable basic.')
	condition_python = fields.Text(string='Python Condition', required=True,
		default='''
					# Available variables:
					#----------------------
					# payslip: object containing the payslips
					# employee: hr.employee object
					# contract: hr.contract object
					# rules: object containing the rules code (previously computed)
					# categories: object containing the computed salary rule categories (sum of amount of all rules belonging to that category).
					# worked_days: object containing the computed worked days
					# inputs: object containing the computed inputs

					# Note: returned value have to be set in the variable 'result'

					result = rules.NET > categories.NET * 0.10''',
		help='Applied this rule for calculation if condition is true. You can specify condition like basic > 1000.')
	condition_range_min = fields.Float(string='Minimum Range', help="The minimum amount, applied for this rule.")
	condition_range_max = fields.Float(string='Maximum Range', help="The maximum amount, applied for this rule.")
	amount_select = fields.Selection([
		('percentage', 'Percentage (%)'),
		('fix', 'Fixed Amount'),
		('code', 'Python Code'),
	], string='Amount Type', index=True, required=True, default='fix', help="The computation method for the rule amount.")
	amount_fix = fields.Float(string='Fixed Amount', digits=dp.get_precision('Payroll'))
	amount_percentage = fields.Float(string='Percentage (%)', digits=dp.get_precision('Payroll Rate'),
		help='For example, enter 50.0 to apply a percentage of 50%')
	amount_python_compute = fields.Text(string='Python Code',
		default='''
					# Available variables:
					#----------------------
					# payslip: object containing the payslips
					# employee: hr.employee object
					# contract: hr.contract object
					# rules: object containing the rules code (previously computed)
					# categories: object containing the computed salary rule categories (sum of amount of all rules belonging to that category).
					# worked_days: object containing the computed worked days.
					# inputs: object containing the computed inputs.

					# Note: returned value have to be set in the variable 'result'

					result = contract.wage * 0.10''')
	amount_percentage_base = fields.Char(string='Percentage based on', help='result will be affected to a variable')
	child_ids = fields.One2many('hr.salary.rule', 'parent_rule_id', string='Child Salary Rule', copy=True)
	register_id = fields.Many2one('hr.contribution.register', string='Contribution Register',
		help="Eventual third party involved in the salary payment of the employees.")
	input_ids = fields.One2many('hr.rule.input', 'input_id', string='Inputs', copy=True)
	note = fields.Text(string='Description')
	analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
	account_tax_id = fields.Many2one('account.tax.code', 'Tax Code')
	account_debit = fields.Many2one('account.account', 'Debit Account')
	account_credit = fields.Many2one('account.account', 'Credit Account')

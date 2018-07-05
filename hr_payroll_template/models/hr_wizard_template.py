from openerp import models, fields, api
import copy


class HrWizardTemplate(models.TransientModel):
	_name = 'hr.wizard.template'

	analytic_account_id = fields.Many2one('account.analytic.account', domain="[('tag','=','cabang')]", string='Analytic Account', required=True)
	job_ids = fields.Many2many('hr.job')

	@api.multi
	def subscribeFuction(self):
		job_cogs = ["DRIV","DRJD","HECE","HELP","HELT","KENE","SIAN","SILK","SIPI","SIPO"]

		rules_exp={
		'BASIC': 215,
		'MEAL': 216,
		'TRANSPORT': 217,
		'PERSISTANCE': 218,
		'TARGET': False,
		'INSENTIF': 219,
		'OPER': 220,
		'ALLOW': 179,
		'BIKE': False,
		'OVERTIME': 221,
		'LOAN': 99,
		'POTHP': 99,
		'POTBRG': 99,
		'PJK_EMP': 247,
		'JHT_EMP': 459,
		'JP_EMP': 459,
		'POTLL': 99,
		'DAILY': 148,
		'EDUCATION': 479,
		'NETD': False,
		}

		rule_analytic_exp ={
			"BASIC"			: "054",
			"MEAL"			: "055",
			"TRANSPORT"		: "056",
			"PERSISTANCE"	: "057",
			"TARGET"		: "",
			"INSENTIF"		: "058",
			"OPER"			: "059",
			"ALLOW"			: "097",
			"BIKE"			: "",
			"OVERTIME"		: "060",
			"LOAN"			: "",
			"POTHP"			: "",
			"POTBRG"		: "",
			"PJK_EMP"		: "",
			"JHT_EMP"		: "",
			"JP_EMP"		: "",
			"POTLL"			: "",	
			"DAILY"			: "",
			"EDUCATION"		: "",
			"NETD"			: "",
		}

		rule_analytic_cogs ={
			"BASIC"			: "008",
			"MEAL"			: "009",
			"TRANSPORT"		: "010",
			"PERSISTANCE"	: "011",
			"TARGET"		: "012",
			"INSENTIF"		: "013",
			"OPER"			: "014",
			"ALLOW"			: "015",
			"BIKE"			: "016",
			"OVERTIME"		: "017",
			"LOAN"			: "",
			"POTHP"			: "",
			"POTBRG"		: "",
			"PJK_EMP"		: "",
			"JHT_EMP"		: "",
			"JP_EMP"		: "",
			"POTLL"			: "",	
			"DAILY"			: "",
			"EDUCATION"		: "",
			"NETD"			: "",
		}

		rules = self.env['hr.payroll.template'].search([])
		payroll_struct = self.env['hr.payroll.structure']

		jobs = []
		for code in self.job_ids:
			jobs.append(code.job_code)

		self.create_rule(jobs,job_cogs,rules_exp,rules,payroll_struct)
		self.create_structure(jobs, job_cogs, rule_analytic_exp, rule_analytic_cogs, rules, payroll_struct)

	def create_rule(self, jobs, job_cogs, rules_exp, rules, payroll_struct):
		for job in jobs:
			struct_code = self.analytic_account_id.code+'-'+job
			struct_name = self.analytic_account_id.name
			struct_id = payroll_struct.search([('code','=',struct_code)])
			if not struct_id:
				base_struct_val = {
				'name':'Base Structure '+job+" "+struct_name,
				'code': struct_code+"_base",
				'company_id':1,
				'rule_ids':[(4,2),(4,3)]
				}
				struct_id_base = payroll_struct.create(base_struct_val)

				struct_val = {
				'name':'Structure '+job+" "+struct_name,
				'code': struct_code,
				'company_id':1,
				'parent_id':struct_id_base.id,
				}
				struct_id=payroll_struct.create(struct_val)

			if struct_id:
				for rule in rules:
					newRule = rule.copy_data()
					rule_cab_name = False
					rule_cab_name = newRule[0]['name']+' ' + job +' cab. '+struct_name
					newRule[0]['name'] = rule_cab_name
					if job not in job_cogs:
						newRule[0]['account_debit'] = rules_exp.get(rule.code)
					rule_id = self.env['hr.salary.rule'].create(newRule[0])

					if rule.code !='BASIC':
						struct_id.write({'rule_ids':[(4,rule_id.id)]})
					else:
						base_struct_code = struct_code+'_base'
						base_struct_id = payroll_struct.search([('code','=',base_struct_code)])
						base_struct_id.write({'rule_ids':[(4,rule_id.id)]})

	def create_structure(self, jobs, job_cogs, rule_analytic_exp, rule_analytic_cogs, rules, payroll_struct):
		for job in jobs:
			struct_code = self.analytic_account_id.code+'-'+job
			struct_name = self.analytic_account_id.name
			struct_id = payroll_struct.search([('code','=',struct_code)])
			if struct_id:
				for rule in rules:
					newRule = rule.copy_data()
					rule_cab_name=False
					rule_cab_name = newRule[0]['name']+' ' + job +' cab. '+struct_name
					analytic=False

					if job not in job_cogs:
						analytic=rule_analytic_exp.get(rule.code)
					else:
						# analytic=rule_analytic_cogs.get('NETD')
						analytic=rule_analytic_cogs.get(rule.code)

					if analytic != "":
						parent_code = struct_code
						code_analytic = struct_code+"-"+analytic
					else:
						code_analytic=False
					rule_id = self.env['hr.salary.rule'].search([('name','=',rule_cab_name)])
					if rule_id and code_analytic :
						analytic_id = self.env['account.analytic.account'].search([('code','=',code_analytic)])						
						if not analytic_id:
							parent_analytic = self.env['account.analytic.account'].search([('code','=',parent_code)])
							if not parent_analytic:
								jabatan = self.env['hr.job'].search([('job_code','=',job)])
								parent_code_pcity = self.analytic_account_id.code
								pcity = self.env['account.analytic.account'].search([('code','=',parent_code_pcity)])
								code_analytic_pcity = parent_code
								analytic_account_pcity = {
								'name': jabatan.name,
								'tag': 'other',
								'type': 'normal',
								'code': code_analytic_pcity,
								'company_id': 1,
								'parent_id': pcity and pcity.id or False,
								}
								# print '====================',analytic_account_pcity,analytic_account_pcity['name']
								parent_analytic = self.env['account.analytic.account'].create(analytic_account_pcity)
							if parent_analytic:
								try:
									parent_analytic=parent_analytic.id
								except:
									parent_analytic=parent_analytic
							analytic_account_new = {
								'name': newRule[0]['name'],
								'tag':'other',
								'type':'normal',
								'code':code_analytic,
								'company_id':1,
								'parent_id':parent_analytic or False,
								}
							analytic_id = self.env['account.analytic.account'].create(analytic_account_new)
						if analytic_id:
							try:
								analytic_id = analytic_id[0]
							except:
								analytic_id=analytic_id

							rule_id.write({'analytic_account_id':analytic_id.id})

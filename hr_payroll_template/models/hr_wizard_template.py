from openerp import models, fields, api
import copy


class HrDepartmentAnalyticAccount(models.Model):
	_inherit = "hr.department"

	analytic_account = fields.Many2one('account.analytic.account', domain="[('tag', 'in', ('gerai', 'cabang', 'toko', 'head_office', 'agen', 'transit', 'pusat_transitan'))]", string='Analytic Account', required=True)	
	struct_ids = fields.Many2many('hr.payroll.structure', 'dept_struct_rel', 'dept_id', 'struct_id', 'Structure Template', domain="[('is_template','=',True)]", required=True)

class HrWizardTemplate(models.TransientModel):
	_name = 'hr.wizard.template'

	department = fields.Many2many('hr.department')
	job_ids = fields.Many2many('hr.job')

	@api.model
	def default_get(self, fields_list):
		context = dict(self._context or {})
		result = super(HrWizardTemplate, self).default_get(fields_list)
		active_job_ids = context.get('active_model') == 'hr.job' and context.get('active_ids') or []
		if active_job_ids:
			result.update({'job_ids':context.get('active_ids')})
		return result

	@api.multi
	def subscribeFuction(self):

		rule_analytic = {
			'500.001.001': '001',
			'500.001.002': '002',
			'500.001.003': '003',
			'500.001.004': '004',
			'500.005.001': '008',
			'500.005.002': '009',
			'500.005.003': '010',
			'500.005.004': '011',
			'500.005.005': '012',
			'500.005.006': '013',
			'500.005.007': '014',
			'500.005.008': '015',
			'500.005.009': '016',
			'500.005.010': '017',
			'600.004.001': '061',
			'600.004.002': '062',
			'600.004.003': '063',
			'600.004.004': '064',
			'500.001.005': '005',
			'500.001.006': '006',
			'500.001.007': '007',
			'500.006.001': '018',
			'500.006.002': '019',
			'500.006.003': '020',
			'500.006.004': '021',
			'500.006.005': '022',
			'500.006.006': '023',
			'500.006.007': '024',
			'500.006.008': '025',
			'500.006.009': '026',
			'500.006.010': '027',
			'500.006.011': '028',
			'500.006.012': '029',
			'500.006.013': '030',
			'500.006.014': '031',
			'500.006.015': '032',
			'500.006.016': '033',
			'500.006.017': '035',
			'500.006.018': '036',
			'500.006.019': '037',
			'500.006.020': '038',
			'500.006.021': '039',
			'500.006.022': '040',
			'500.006.023': '041',
			'500.007.001': '034',
			'600.001.001': '051',
			'600.002.001': '052',
			'600.002.002': '053',
			'600.003.001': '054',
			'600.003.002': '055',
			'600.003.003': '056',
			'600.003.004': '057',
			'600.003.005': '058',
			'600.003.006': '059',
			'600.003.007': '060',
			'600.004.005': '065',
			'600.004.006': '066',
			'600.004.007': '067',
			'600.004.008': '068',
			'600.004.009': '069',
			'600.004.010': '070',
			'600.004.011': '071',
			'600.004.012': '072',
			'600.004.013': '073',
			'600.004.014': '074',
			'600.004.015': '075',
			'600.004.016': '076',
			'600.004.017': '077',
			'600.004.018': '078',
			'600.004.019': '079',
			'600.004.020': '080',
			'600.004.021': '081',
			'600.004.022': '082',
			'600.005.001': '083',
			'600.005.002': '084',
			'600.006.001': '085',
			'600.006.002': '086',
			'600.007.001': '087',
			'600.008.001': '088',
			'600.008.002': '089',
			'600.009.001': '090',
			'600.009.002': '091',
			'600.009.003': '092',
			'600.009.004': '093',
			'800.001.001': '094',
			'800.002.000': '095',
			'800.003.000': '096',
			'600.005.003': '098',
			'600.003.010': '099',
			'112.002.000': '100',
		}

		payroll_struct = self.env['hr.payroll.structure']
		
		jobs = []
		for code in self.job_ids:
			jobs.append(code.job_code)

		base_code = ["BASIC","GROSS","NET","NETD","TDED"]
		self.create_rule_structure(base_code, jobs, payroll_struct)
		self.create_analytic_account(base_code, jobs, rule_analytic, payroll_struct)

	def create_rule_structure(self, base_code, jobs, payroll_struct):
		for dept in self.department:
			for job in jobs:
				struct_code = dept.analytic_account.code+'-'+job
				struct_name = dept.analytic_account.name
				
				for struct in dept.struct_ids:
					struct_id = payroll_struct.search([('code','=',struct_code)])
					if not struct_id:
						base_struct_val = {
						'name':'Base Structure '+job+" "+struct_name,
						'code': struct_code+"_base",
						'company_id':1,
						'parent_id': False,
						}
						struct_id_base = payroll_struct.create(base_struct_val)

						struct_val = {
						'name':'Structure '+job+" "+struct_name,
						'code': struct_code,
						'company_id':1,
						'parent_id':struct_id_base.id,
						}
						struct_record = payroll_struct.create(struct_val)

					if struct_id:
						for struct in dept.struct_ids:
							newRule = struct.rule_ids.copy_data()
							for rule in newRule:
								rule['is_template'] = False
								rule_name = False
								rule_name = rule['name'] + ' ' + job + ' Cab. ' + struct_name
								rule['name'] = rule_name
								rule_id = self.env['hr.salary.rule'].create(rule)

								if rule['code'] not in base_code:
									struct_id.write({"rule_ids":[(4,rule_id.id)]})
								else:
									base_struct_code = struct_code+'_base'
									base_struct_id = payroll_struct.search([('code','=',base_struct_code)])
									base_struct_id.write({'rule_ids':[(4,rule_id.id)]})

	def create_analytic_account(self, base_code, jobs, rule_analytic, payroll_struct):
		for dept in self.department:
			for job in jobs:
				struct_code = dept.analytic_account.code+'-'+job
				struct_code_base = dept.analytic_account.code+'-'+job+'_base'
				struct_name = dept.analytic_account.name
				struct_ids = payroll_struct.search([('code','in',(struct_code, struct_code_base))])

				if struct_ids:
					for struct in struct_ids:
						for rule in struct.rule_ids:

							if rule.account_debit:
								analytic = False
								analytic = rule_analytic.get(rule.account_debit.code)

								if analytic or analytic != None:
									parent_code = struct_code
									code_analytic = struct_code+"-"+analytic
								else:
									code_analytic = False

								if code_analytic:
									analytic_id = self.env['account.analytic.account'].search([('code','=',code_analytic)])

									if not analytic_id:
										parent_analytic = self.env['account.analytic.account'].search([('code','=',parent_code)])

										if not parent_analytic:
											jabatan = self.env['hr.job'].search([('job_code','=',job)])
											parent_code_pcity = dept.analytic_account.code
											pcity = self.env['account.analytic.account'].search([('code','=',parent_code_pcity)])
											code_analytic_pcity = parent_code
											analytic_account_pcity = {
											'name': jabatan.name,
											'tag': 'other',
											'type': 'normal',
											'code':code_analytic_pcity,
											'company_id': 1,
											'parent_id': pcity and pcity.id or False,
											}
											parent_analytic = self.env['account.analytic.account'].create(analytic_account_pcity)

										if parent_analytic:
											try:
												parent_analytic=parent_analytic.id
											except:
												parent_analytic=parent_analytic

										analytic_account_new = {
											'name': rule.name,
											'tag':'other',
											'type':'normal',
											'code':code_analytic,
											'company_id':1,
											'parent_id':parent_analytic or False,
											}
										analytic_id = self.env['account.analytic.account'].create(analytic_account_new)

									if analytic_id:
										rule.write({'analytic_account_id':analytic_id.id})

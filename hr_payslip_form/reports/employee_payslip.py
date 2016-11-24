from openerp.osv import osv
from openerp.report import report_sxw
from openerp.addons.hr_payroll.report.report_payslip import payslip_report

class payslip_report_inherit(payslip_report):

	def __init__(self, cr, uid, name, context):
		super(payslip_report_inherit, self).__init__(cr, uid, name, context)
		self.localcontext.update({
			'get_thp': self.get_thp,
		})

	def get_thp(self, obj):
		payslip_line = self.pool.get('hr.payslip.line')
		res = []
		ids = []
		for id in range(len(obj)):
			if obj[id].appears_on_payslip is True:
				ids.append(obj[id].id)
		if ids:
			res = payslip_line.browse(self.cr, self.uid, ids)
			thp = 0.0
			for line in res:
				if line.code == 'NET':
					thp += line.total or 0.0
		return thp

class wrapped_report_payslip(osv.AbstractModel):
	_name = 'report.hr_payroll.report_payslip'
	_inherit = 'report.abstract_report'
	_template = 'hr_payroll.report_payslip'
	_wrapped_report_class = payslip_report_inherit
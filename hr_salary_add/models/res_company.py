from openerp.osv import fields,osv

class res_company(osv.osv):
	_inherit = "res.company"

	_columns = {
		"piutang_hp_loan_type_id": fields.many2one('hr.loan.type',"Piutang HP Default Loan Type"),
	}
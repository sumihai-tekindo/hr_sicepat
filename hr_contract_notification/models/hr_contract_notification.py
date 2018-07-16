
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp import api, fields, models

class HRContractNotification(models.Model):
	_inherit = ['ir.needaction_mixin', 'hr.contract']
	_name = 'hr.contract'

	@api.model
	def _needaction_domain_get(self):
		now = datetime.now().strftime('%Y-%m-%d')
		notif_month = (datetime.now() + relativedelta(months=1)).strftime('%Y-%m-%d')
		return [('trial_date_end','>=',now),('trial_date_end','<=',notif_month)]
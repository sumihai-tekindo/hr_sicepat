import re
import time
import datetime
import math

from openerp import api, fields as fields2
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools import float_round, float_is_zero, float_compare
from openerp.tools.translate import _
import simplejson as json
from dateutil.relativedelta import relativedelta


class stock_hr_loan(osv.osv):
	_name = "stock.hr.loan"

	def _current_rate(self, cr, uid, ids, name, arg, context=None):
		return self._get_current_rate(cr, uid, ids, context=context)

	def _current_rate_silent(self, cr, uid, ids, name, arg, context=None):
		return self._get_current_rate(cr, uid, ids, raise_on_no_rate=False, context=context)

	def _get_current_rate(self, cr, uid, ids, raise_on_no_rate=True, context=None):
		if context is None:
			context = {}
		res = {}

		date = context.get('date') or fields2.Datetime.now()
		for id in ids:
			cr.execute('SELECT nilai_piutang FROM stock_hr_loan_line '
                       'WHERE loan_id = %s '
                         'AND tanggal_berlaku <= %s '
                       'ORDER BY tanggal_berlaku desc LIMIT 1',
                       (id, date))
			if cr.rowcount:
				res[id] = cr.fetchone()[0]
			elif not raise_on_no_rate:
				res[id] = 0
			else:
				currency = self.browse(cr, uid, id, context=context)
				raise osv.except_osv(_('Error!'),_("No currency rate associated for currency '%s' for the given period" % (currency.name)))
		return res

	_columns = {
		'name': fields.char('Name',required=True),
		'rate': fields.function(_current_rate, string='Rate', digits=(6,2),
            help='The rate of the currency to the currency of rate 1.'),
		'rate_silent': fields.function(_current_rate_silent, string='Current Rate', digits=(6,2),
            help='The rate of the currency to the currency of rate 1 (0 if no rate defined).'),
		'line_ids': fields.one2many('stock.hr.loan.line','loan_id',"Lines"),
		'account_id': fields.many2one('account.account',"Accounts",required=True),
	}


class stock_hr_loan_line(osv.osv):
	_name = "stock.hr.loan.line"

	_columns = {
		"tanggal_berlaku": fields.date('Date', required=True, select=True),
		"nilai_piutang": fields.float("Nilai Piutang" ,required=True),
		"loan_id": fields.many2one('stock.hr.loan',"Loan",readonly=True),
	}


class hr_loan(osv.osv):
	_inherit = "hr.loan"

	def _compute_selisih(self, cr, uid, ids, name, arg, context=None):
		res = {} 

		if not ids:
			ids = self.search(cr,uid,[],context=context)
		
		for rec in self.browse(cr,uid,ids,context=context):
			res[rec.id] = rec.nilai_pinjaman - rec.original 

		return res

	_columns = {
		'original': fields.float("Nilai Pinjaman Original",required=True),
		'selisih': fields.function(_compute_selisih, string="Selisih pengakuan piutang HP",required=True),
	}



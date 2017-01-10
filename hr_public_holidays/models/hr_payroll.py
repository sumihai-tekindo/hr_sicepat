import datetime
from datetime import timedelta
from dateutil import rrule
from dateutil.relativedelta import relativedelta
from operator import itemgetter

from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.float_utils import float_compare
from openerp.tools.translate import _
import pytz
from openerp.addons.resource.resource import seconds

class resource_calendar(osv.osv):
	_inherit = "resource.calendar"

	def get_working_hours_of_date(self, cr, uid, id, start_dt=None, end_dt=None,leaves=None,compute_leaves=False,resource_id=None,default_interval=None, context=None):
		""" Get the working hours of the day based on calendar. This method uses
		get_working_intervals_of_day to have the work intervals of the day. It
		then calculates the number of hours contained in those intervals. """
		
		date_holiday = start_dt.strftime('%Y-%m-%d')
		is_holiday = self.pool.get('hr.holidays.public.line').search(cr,uid,[('date','=',date_holiday)])
		if is_holiday:
			return 0.0
		intervalx = super(resource_calendar,self).get_working_hours_of_date(cr, uid, id, start_dt=start_dt, end_dt=end_dt,leaves=leaves,compute_leaves=compute_leaves,resource_id=resource_id,default_interval=default_interval, context=context)
		res = datetime.timedelta()
		intervals = self.get_working_intervals_of_day(cr, uid, id, start_dt, end_dt, leaves,compute_leaves, resource_id,default_interval, context)
		for interval in intervals:
			res += interval[1] - interval[0]

		return seconds(res) / 3600.0


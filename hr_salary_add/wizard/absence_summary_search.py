# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017 Sicepat Ekspres Indonesia (<http://www.sicepat.com>).
#    @author: - Pambudi Satria <pambudi.satria@yahoo.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# 1 : imports of python lib
from datetime import datetime
from dateutil.relativedelta import relativedelta

# 2 :  imports of openerp
from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp.tools.translate import _
from openerp.tools.misc import DEFAULT_SERVER_DATE_FORMAT

# 3 :  imports from odoo modules
import openerp.addons.decimal_precision as dp

class HRLoanLineUnpaidWizard(models.TransientModel):
    """
    This wizard will show all absence summary based on given dates and department
    """

    _name = "hr.absence.summary.search_wizard"
    _description = "Show absence summary based on given dates and department"
    
    date_start = fields.Date(string="Start Date", required=True, default=lambda *a: str(datetime.now() + relativedelta(months=-1, day=21))[:10])
    date_end = fields.Date(string="End Date", required=True, default=lambda *a: str(datetime.now() + relativedelta(day=20))[:10])
    department_ids = fields.Many2many('hr.department', 'absence_summary_department_rel', 'absence_summary_id', 'dept_id', string='Departments')

    @api.multi
    def search_absence_summary(self):
        self.ensure_one()
        for record in self:
            department_ids = [dept.id for dept in record.department_ids] or [dept.id for dept in self.env['hr.department'].search([])]
            domain_1 = [('department_id', 'in', department_ids)]
            domain_2 = [('periode', '>=', record.date_start), ('periode', '<=', record.date_end)]
            records = self.env['hr.absence.summary'].search(domain_1 + domain_2)
        action = self.env['ir.model.data'].get_object_reference('hr_salary_add', 'absence_summary_action')
        act_id = action and action[1] or False
        result = self.env['ir.actions.act_window'].browse([act_id]).read()[0]
        result['domain'] = str([('id', 'in', [rec.id for rec in records])])
        result['context'] = str({'search_default_group_by_department':1,'search_default_group_by_employee':1})
        return result

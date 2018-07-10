# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Sicepat Ekspres Indonesia (<http://www.sicepat.com>).
#    @author: - Timotius Wigianto <https://github.com/timotiuswigianto/>
#             - Pambudi Satria <pambudi.satria@yahoo.com>
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

# 2 :  imports of openerp
from openerp import models, fields, api

# 3 :  imports from odoo modules
import openerp.addons.decimal_precision as dp

class HRPayslipRun(models.Model):
    # Private attributes
    _inherit = 'hr.payslip.run'

    # Default methods
    

    # Fields declaration
    total_amount = fields.Float(digits=dp.get_precision('Payroll'), string='Total Amount', compute='_compute_total_amount', store=True)

    # compute and search fields, in the same order that fields declaration
    @api.one
    @api.depends('slip_ids.net_amount')
    def _compute_total_amount(self):
        total = 0.0
        for slip in self.slip_ids:
            total += slip.net_amount
        self.total_amount = total

    # Constraints and onchanges

    # CRUD methods

    # Action methods

    # Business methods

class HRPayslip(models.Model):
    # Private attributes
    _inherit = 'hr.payslip'

    # Default methods
    

    # Fields declaration
    net_amount = fields.Float(digits=dp.get_precision('Payroll'), string='Net Amount', compute='_compute_net_amount', store=True)

    # compute and search fields, in the same order that fields declaration
    @api.one
    @api.depends('line_ids.code', 'line_ids.total')
    def _compute_net_amount(self):
        amount = 0.0
        for l in self.line_ids:
            if l.code == 'NET':
                amount += l.total
        self.net_amount = amount

    # Constraints and onchanges
#     def onchange_employee_id(self, cr, uid, ids, date_from, date_to, employee_id=False, contract_id=False, context=None):
#         contract_obj = self.pool.get('hr.contract')
#         if context is None:
#             context = {}
# 
#         res = super(HRPayslip, self).onchange_employee_id(cr, uid, ids, date_from, date_to, \
#             employee_id=employee_id, contract_id=contract_id, context=context)
# 
#         contract_ids = res.get('value', {}) and res.get('value').get('contract_id', False)
#         
#         if contract_ids:
#             contract = contract_obj.browse(cr, uid, contract_ids, context=context)
#             if contract.date_start and contract.date_start >= date_from:
#                 date_from = contract.date_start
#             if contract.date_end and contract.date_end <= date_to:
#                 date_to = contract.date_end
#             new_worked_days_line = self.get_worked_day_lines(cr, uid, contract_ids, date_from, date_to, context=context)
#             worked_days_line_ids = res.get('value', {}) and res.get('value').get('worked_days_line_ids', [])
#             if new_worked_days_line:
#                 new_worked_days_line[0]['code'] = 'WORKING'
#                 worked_days_line_ids += new_worked_days_line 
#         
#         return res

    # CRUD methods

    # Action methods
    @api.multi
    def hr_verify_sheet(self):
        self.state = 'verify'

    # Business methods

    class HrDepartmentCode(models.Model):
        _inherit = "hr.department"

        department_code = fields.Char('Department Code')
        ojt_rule = fields.Boolean()

    class BankAccountHistory(models.Model):
        _inherit = ['mail.thread', 'res.partner.bank']
        _name = 'res.partner.bank'
        
        acc_number = fields.Char(track_visibility='onchange')
        bank = fields.Many2one('res.bank', 'Bank', track_visibility='onchange')
        bank_name = fields.Char(track_visibility='onchange')
        owner_name = fields.Char(track_visibility='onchange')
        partner_id = fields.Many2one('res.partner', 'Account Owner', ondelete='cascade', select=True, domain=['|',('is_company','=',True),('parent_id','=',False)], track_visibility='onchange')
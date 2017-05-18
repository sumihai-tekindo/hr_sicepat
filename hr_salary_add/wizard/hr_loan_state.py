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
from datetime import datetime
from dateutil.relativedelta import relativedelta

# 2 :  imports of openerp
from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp.tools.translate import _
from openerp.tools.misc import DEFAULT_SERVER_DATE_FORMAT

# 3 :  imports from odoo modules
import openerp.addons.decimal_precision as dp

class HRLoanSubmit(models.TransientModel):
    """
    This wizard will submit the all the selected open loan
    """

    _name = "hr.loan.submit"
    _description = "Submit the selected loan"

    @api.multi
    def loan_submit(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['hr.loan'].browse(active_ids):
            if record.state not in ('draft'):
                raise Warning(_("Selected loan(s) cannot be submitted as they are not in 'Open' state."))
            record.action_submit()
            
        return {'type': 'ir.actions.act_window_close'}

class HRLoanApprove(models.TransientModel):
    """
    This wizard will approve the all the selected submit loan
    """

    _name = "hr.loan.approve"
    _description = "Approve the selected loan"

    @api.multi
    def loan_approve(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['hr.loan'].browse(active_ids):
            if record.state not in ('submit'):
                raise Warning(_("Selected loan(s) cannot be approved as they are not in 'Submit' state."))
            record.action_approve()
            
        return {'type': 'ir.actions.act_window_close'}

class HRLoanRejectWizard(models.TransientModel):
    _name = "hr.loan.reject_wizard"
    _description = "Loan Reject Wizard"
    
    @api.model
    def _default_loan_ids(self):
        context = dict(self._context or {})
        loan_model = self.env['hr.loan']
        loan_ids = context.get('active_model') == 'hr.loan' and context.get('active_ids') or []
        return [
            (0, 0, {'loan_id': loan.id, 'employee_id': loan.employee_id.id, 'loan_type': loan.loan_type.id, 'nilai_pinjaman': loan.nilai_pinjaman})
            for loan in loan_model.browse(loan_ids)
        ]

    loan_ids = fields.One2many('hr.loan.reject', 'wizard_id', string='Loan', default=_default_loan_ids)
    
    @api.multi
    def reject_loan_button(self):
        for line in self.loan_ids:
            if line.loan_id.state not in ('submit'):
                raise Warning(_('You cannot reject loan which is not Submit. You should submit it instead.'))
        line_ids = [line.id for line in self.loan_ids]
        self.env['hr.loan.reject'].browse(line_ids).reject_button()
        return {'type': 'ir.actions.act_window_close'}

class HRLoanReject(models.TransientModel):
    _name = "hr.loan.reject"
    _description = "Loan Reject"
    
    wizard_id = fields.Many2one('hr.loan.reject_wizard', string='Wizard', required=True)
    loan_id = fields.Many2one('hr.loan', string='Loan', required=True, readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Nama Karyawan', required=True, readonly=True)
    loan_type = fields.Many2one('hr.loan.type', string='Loan Type', required=True, readonly=True)
    nilai_pinjaman = fields.Float(digits=dp.get_precision('Payroll'), string='Nilai Pinjaman', required=True, readonly=True)
    alasan_reject = fields.Text('Alasan Reject')
    
    @api.multi
    def reject_button(self):
        for loan in self:
            loan.loan_id.write({'alasan_reject': loan.alasan_reject})
            loan.loan_id.action_reject()
        # don't keep temporary notes in the database longer than necessary
        self.write({'alasan_reject': False})

class HRLoanCloseWizard(models.TransientModel):
    _name = "hr.loan.close_wizard"
    _description = "Loan Close Wizard"
    
    @api.model
    def default_get(self, fields_list):
        context = dict(self._context or {})
        result = super(HRLoanCloseWizard, self).default_get(fields_list)
        loan_model = self.env['hr.loan']
        loan_ids = context.get('active_model') == 'hr.loan' and context.get('active_ids') or []
        result.update({'loan_ids':
            [(0, 0, {'loan_id': loan.id, 'employee_id': loan.employee_id.id, 'loan_type': loan.loan_type.id, 'nilai_pinjaman': loan.nilai_pinjaman})
            for loan in loan_model.browse(loan_ids)]
        })
        return result

    loan_ids = fields.One2many('hr.loan.close', 'wizard_id', string='Loan')
    
    @api.multi
    def close_loan_button(self):
        line_ids = [line.id for line in self.loan_ids]
        self.env['hr.loan.close'].browse(line_ids).close_button()
        return {'type': 'ir.actions.act_window_close'}

class HRLoanClose(models.TransientModel):
    _name = "hr.loan.close"
    _description = "Loan Close"
    
    @api.model
    def default_get(self, fields_list):
        context = dict(self._context or {})
        result = super(HRLoanClose, self).default_get(fields_list)
        loan_ids = context.get('active_model') == 'hr.loan' and context.get('active_ids') or []
        loan = self.env['hr.loan'].browse(loan_ids)
        result.update({'loan_id': loan.id, 'employee_id': loan.employee_id.id, 'loan_type': loan.loan_type.id, 'nilai_pinjaman': loan.nilai_pinjaman})
        return result
        
    wizard_id = fields.Many2one('hr.loan.close_wizard', string='Wizard', required=True)
    loan_id = fields.Many2one('hr.loan', string='Loan', required=True, readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Nama Karyawan', required=True, readonly=True)
    loan_type = fields.Many2one('hr.loan.type', string='Loan Type', required=True, readonly=True)
    nilai_pinjaman = fields.Float(digits=dp.get_precision('Payroll'), string='Nilai Pinjaman', required=True, readonly=True)
    notes = fields.Text('Notes')
    
    @api.multi
    def close_button(self):
        for loan in self:
            loan.loan_id.write({'notes': loan.loan_id.notes and loan.loan_id.notes + '\n' + loan.notes or loan.notes})
            loan.loan_id.action_close()
        # don't keep temporary notes in the database longer than necessary
        self.write({'notes': False})

class HRLoanLinePost(models.TransientModel):
    """
    This wizard will post the all the selected loan line
    """

    _name = "hr.loan.line.post"
    _description = "Post the selected loan line"

    @api.multi
    def loan_line_post(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['hr.loan.line'].browse(active_ids):
            if record.posted:
                raise Warning(_("Selected loan line(s) cannot be post as they are already 'Posted'."))
            record.action_post()
            
        return {'type': 'ir.actions.act_window_close'}

class HRLoanLineUnpaidWizard(models.TransientModel):
    """
    This wizard will show all unpaid loan line based on date and department given
    """

    _name = "hr.loan.line.search_wizard"
    _description = "Show all unpaid loan line"
    
    date_start = fields.Date(string="Start Date", required=True, default=lambda *a: str(datetime.now() + relativedelta(months=-1, day=21))[:10])
    date_end = fields.Date(string="End Date", required=True, default=lambda *a: str(datetime.now() + relativedelta(day=20))[:10])
    department_ids = fields.Many2many('hr.department', 'loan_line_unpaid_department_rel', 'loan_line_unpaid_id', 'dept_id', string='Departments')

    @api.multi
    def search_loan_line(self):
        self.ensure_one()
#         context = dict(self._context or {})
#         mod_obj = self.env['ir.model.data']
        for record in self:
            department_ids = [dept.id for dept in record.department_ids] or [dept.id for dept in self.env['hr.department'].search([])]
            loan_domain = [('department_id', 'in', department_ids)]
            loan_ids = [loan.id for loan in self.env['hr.loan'].search(loan_domain)]
            loan_line_domain_1 = [('loan_id', 'in', loan_ids), ('paid', '=', False)]
            loan_line_domain_2 = [('tanggal_angsuran', '>=', record.date_start), ('tanggal_angsuran', '<=', record.date_end)]
            loan_line_ids = self.env['hr.loan.line'].search(loan_line_domain_1 + loan_line_domain_2)
        action = self.env['ir.model.data'].get_object_reference('hr_salary_add', 'unpaid_loan_action')
        act_id = action and action[1] or False
        result = self.env['ir.actions.act_window'].browse([act_id]).read()[0]
        result['domain'] = str([('id', 'in', [l.id for l in loan_line_ids])])
        return result
#         form_id = mod_obj.get_object_reference('hr_salary_add', 'unpaid_loan_line_form_view')
#         form_res = form_id and form_id[1] or False
#         tree_id = mod_obj.get_object_reference('hr_salary_add', 'unpaid_loan_line_tree_view')
#         tree_res = tree_id and tree_id[1] or False
#         return {
#             'name':_("Unpaid Installment"),
#             'view_mode': 'tree, form',
#             'view_id': False,
#             'view_type': 'form',
#             'res_model': 'hr.loan.line',
#             'type': 'ir.actions.act_window',
#             'nodestroy': True,
#             'target': 'current',
#             'domain': "[('id', 'in', %s)]" % [l.id for l in loan_line_ids],
#             'views': [(tree_res, 'tree'), (form_res, 'form')],
#             'context': context,
#         }

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
from openerp.osv import osv
from openerp.tools.translate import _
from openerp.tools.misc import DEFAULT_SERVER_DATE_FORMAT

# 3 :  imports from odoo modules
import openerp.addons.decimal_precision as dp
# from .hr_salary_structure_amt import CODE2INPUT
# CODE2INPUT['CLOAN']='nilai_pinjaman'
# CODE2INPUT['LOAN']='nilai_angsuran'
CODE2INPUT = {
    'CLOAN': 'nilai_pinjaman',
    'LOAN': 'nilai_angsuran',
}
class HRLoanType(models.Model):
    _name="hr.loan.type"
    name = fields.Char(string='Number', readonly=False)


class HRLoan(models.Model):
    # Private attributes
    _name = "hr.loan"
    _inherit = ['mail.thread']
    _description= 'HR Loan'
    _order = "tanggal desc, id desc"

    # Default methods
    

    # Fields declaration
    name = fields.Char(string='Number', readonly=True)
    loan_type=fields.Many2one('hr.loan.type', 'Loan Type')
    tanggal = fields.Date(default=lambda self: fields.Date.context_today(self), readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    employee_id = fields.Many2one('hr.employee', 'Nama Karyawan', required=True, readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    jabatan_id = fields.Many2one('hr.job', string='Jabatan')
    department_id = fields.Many2one('hr.department', string='Nama Cabang')
    jabatan_id_view = fields.Many2one('hr.job', string='Jabatan', compute='_compute_field_view', readonly=True)
    department_id_view = fields.Many2one('hr.department', string='Nama Cabang', compute='_compute_field_view', readonly=True)
    address_home_id = fields.Many2one('res.partner', string='Home Address', related='employee_id.address_home_id', readonly=True)
    pinjaman_unpaid = fields.Float(digits=dp.get_precision('Payroll'), string="Pinjaman Sebelumnya", compute='_compute_pinjaman_unpaid')
#     type = fields.Selection([
#         ('loan', 'Pinjaman'),
#         ('expense', 'Biaya'),
#         ('phone', 'Handphone')
#         ], 'Tipe', default='loan', states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    nilai_pinjaman = fields.Float(digits=dp.get_precision('Payroll'), string='Nilai Pinjaman', required=True, readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    tenor_angsuran = fields.Integer(string='Tenor', required=True, default=1, help="Lama angsuran dalam bulan", readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    nilai_angsuran = fields.Float(digits=dp.get_precision('Payroll'), string="Angsuran Per Bulan", compute='_compute_angsuran_per_bulan', readonly=True)
    total_angsuran = fields.Float(digits=dp.get_precision('Payroll'), string="Total Angsuran", compute='_compute_angsuran')
    total_bayar_angsuran = fields.Float(digits=dp.get_precision('Payroll'), string="Total Pembayaran Angsuran", compute='_compute_angsuran')
    sisa_angsuran = fields.Float(digits=dp.get_precision('Payroll'), string="Sisa Angsuran", compute='_compute_angsuran')
    tanggal_awal_angsuran = fields.Date(string="Tanggal mulai angsuran", required=True, default=lambda *a: str(datetime.now() + relativedelta(day=20))[:10], readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    notes = fields.Text(readonly=True, states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    loan_line = fields.One2many('hr.loan.line', 'loan_id', index=True)
    alasan_reject = fields.Text(readonly=True, states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    payment_method = fields.Selection([
        ('bank', 'Bank Transfer'),
        ('cash', 'Tunai'),
        ('other', 'Lain-lain')
        ], string='Payment method', default='bank',
        readonly=True, states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    bank_account_id = fields.Many2one('res.partner.bank', 'Rekening', domain="[('partner_id','=',address_home_id)]",
        readonly=True, states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    state = fields.Selection([
        ('draft','Open'),
        ('submit','Submit'),
        ('reject','Reject'),
        ('approved','Approved'),
        ], string='Status', default='draft', track_visibility='onchange', copy=False,)
    
    # compute and search fields, in the same order that fields declaration
    @api.one
    @api.depends('jabatan_id','department_id')
    def _compute_field_view(self):
        self.jabatan_id_view = self.jabatan_id.id
        self.department_id_view = self.department_id.id
        
    @api.one
    @api.depends('employee_id','state')
    def _compute_pinjaman_unpaid(self):
        unpaid_amount = 0.0
        for loan in self.search([('employee_id','=',self.employee_id.id),('state','=','approved')]):
            if loan.id != self.id:
                unpaid_amount += loan.sisa_angsuran
        self.pinjaman_unpaid = unpaid_amount
        
    @api.one
    @api.depends('nilai_pinjaman','tenor_angsuran')
    def _compute_angsuran_per_bulan(self):
#         if((self.nilai_pinjaman!=0) and (self.tenor_angsuran!=0)):
#             self.nilai_angsuran = self.nilai_pinjaman/self.tenor_angsuran
        try:
            nilai_angsuran = self.nilai_pinjaman/self.tenor_angsuran
        except:
            nilai_angsuran = 0.0
        self.nilai_angsuran = nilai_angsuran

    @api.one
    @api.depends('nilai_pinjaman','loan_line.nilai_angsuran','loan_line.paid')
    def _compute_angsuran(self):
#         total_paid_amount = 0.00
#         for loan in self:
#             for line in loan.loan_line:
#                 if line.paid == True:
#                     total_paid_amount += line.nilai_angsuran
#             
#             balance_amount = loan.nilai_pinjaman - total_paid_amount
#             self.total_angsuran = loan.nilai_pinjaman
#             self.sisa_angsuran = balance_amount
#             self.total_bayar_angsuran = total_paid_amount
        self.total_angsuran = self.nilai_pinjaman
        self.total_bayar_angsuran = sum(line.nilai_angsuran for line in self.loan_line if line.paid)
        self.sisa_angsuran = self.total_angsuran - self.total_bayar_angsuran 
            
    # Constraints and onchanges
    @api.multi
    def payment_method_change(self, payment_method):
        if payment_method and payment_method != 'bank':
            return {'value': {'bank_account_id': False}}

    @api.onchange('employee_id')
    def onchange_employee(self):
        self.jabatan_id = self.employee_id.job_id.id
        self.department_id = self.employee_id.department_id.id

    # CRUD methods
    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].get('hr.loan') or ' '
        return super(HRLoan, self).create(values)

    # Action methods
    @api.multi
    def action_submit(self):
        self.state = 'submit'

    @api.multi
    def action_approve(self):
        for loan in self:
            date_start_str = datetime.strptime(loan.tanggal_awal_angsuran, DEFAULT_SERVER_DATE_FORMAT)
            for count in range(0, loan.tenor_angsuran):
                self.env['hr.loan.line'].create({
                    'tanggal_angsuran': date_start_str, 
                    'nilai_angsuran': loan.nilai_angsuran,
                    'loan_id': loan.id
                })
                date_start_str = date_start_str + relativedelta(months=1)
        self.state = 'approved'
        
    @api.multi
    def action_reject(self):
        self.state = 'reject'
        
#     @api.multi
#     def compute_loan_line(self):
#         loan_line = self.env['hr.loan.line']
#         loan_line.search([('loan_id','=',self.id)]).unlink()
#         for loan in self:
#             date_start_str = datetime.strptime(loan.tanggal_awal_angsuran, DEFAULT_SERVER_DATE_FORMAT)
#             for count in range(1, loan.tenor_angsuran + 1):
#                 loan_line.create({
#                     'tanggal_angsuran': date_start_str, 
#                     'nilai_angsuran': loan.nilai_angsuran,
#                     'loan_id': loan.id
#                 })
#                 date_start_str = date_start_str + relativedelta(months=1)
#         return True

    # Business methods
    def get_loan(self, cr, uid, employee, date_from, date_to, context=None):
        """
        @param employee: browse record of employee
        @param date_from: date field
        @param date_to: date field
        @return: returns the ids of all the salary structure lines for the given employee that need to be considered for the given dates
        """
        clause_1 = ['&',('tanggal', '<=', date_to),('tanggal','>=', date_from)]
        clause_final = [('employee_id','=',employee.id), ('state','=','approved')] + clause_1
        loan_ids = self.search(cr, uid, clause_final, order='tanggal desc', context=context)
        return loan_ids

    def get_amount(self, cr, uid, ids, code, context=None):
        """
        @param code: char field
        @return: returns amount based on code
        """
        loan = self.browse(cr, uid, ids, context)
        amt = 0.0
        for l in loan:
            amt+=l[CODE2INPUT.get(code)]
        return amt

    def get_condition(self, cr, uid, code, context=None):
        """
        @param code: char field
        @return: returns True or False
        """
        if code:
            if code in CODE2INPUT:
                return True
        return False

class HRLoanLine(models.Model):
    # Private attributes
    _name = "hr.loan.line"
    
    # Default methods
    

    # Fields declaration
    loan_id = fields.Many2one('hr.loan', string="Loan #", ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', 'Nama Karyawan', related='loan_id.employee_id')
    tanggal_angsuran = fields.Date(string='Tanggal Angsuran', required=True)
    nilai_angsuran = fields.Float(digits=dp.get_precision('Payroll'), string='Nilai Angsuran')
    total_nilai_angsuran = fields.Float(digits=dp.get_precision('Payroll'), string='Total Nilai Angsuran')
    sisa_angsuran = fields.Float(digits=dp.get_precision('Payroll'), string='Sisa Angsuran')
    keterangan = fields.Text(string='Notes')
    posted = fields.Boolean()
    paid = fields.Boolean()

    # compute and search fields, in the same order that fields declaration


    # Constraints and onchanges


    # CRUD methods


    # Action methods
    @api.multi
    def action_post(self):
        self.posted = True
        
    @api.multi
    def action_undo_post(self):
        self.posted = False

    # Business methods
    def get_loan_line(self, cr, uid, employee, date_from, date_to, context=None):
        """
        @param employee: browse record of employee
        @param date_from: date field
        @param date_to: date field
        @return: returns the ids of all the salary structure lines for the given employee that need to be considered for the given dates
        """
        clause_1 = ['&',('tanggal_angsuran', '<=', date_to),('tanggal_angsuran','>=', date_from)]
        clause_final = [('employee_id','=',employee.id), ('posted','=',True), ('paid','=',False)] + clause_1
        loan_line_ids = self.search(cr, uid, clause_final, order='tanggal_angsuran desc', context=context)
        return loan_line_ids

    def get_amount(self, cr, uid, ids, code, context=None):
        """
        @param code: char field
        @return: returns amount based on code
        """
#         loan_line = self.browse(cr, uid, ids, context)
#         return loan_line[0][CODE2INPUT.get(code)]
        amount = 0.0
        for loan_line in self.browse(cr, uid, ids, context):
            amount += loan_line[CODE2INPUT.get(code)]
        return amount

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
            (0, 0, {'loan_id': loan.id, 'employee_id': loan.employee_id.id, 'nilai_pinjaman': loan.nilai_pinjaman})
            for loan in loan_model.browse(loan_ids)
        ]

    loan_ids = fields.One2many('hr.loan.reject', 'wizard_id', string='Loan', default=_default_loan_ids)
    
    @api.multi
    def reject_loan_button(self):
        line_ids = []
        for line in self.loan_ids:
            if line.loan_id.state not in ('submit'):
                raise Warning(_('You cannot reject loan which is not Submit. You should submit it instead.'))
            line_ids.append(line.id)
#         line_ids = [line.id for line in self.loan_ids]
        self.env['hr.loan.reject'].reject_button(line_ids)
        return {'type': 'ir.actions.act_window_close'}

class HRLoanReject(models.TransientModel):
    _name = "hr.loan.reject"
    _description = "Loan Reject"
    
    wizard_id = fields.Many2one('hr.loan.reject_wizard', string='Wizard', required=True)
    loan_id = fields.Many2one('hr.loan', string='Loan', required=True, readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Nama Karyawan', required=True, readonly=True)
    nilai_pinjaman = fields.Float(digits=dp.get_precision('Payroll'), string='Nilai Pinjaman', required=True, readonly=True)
    alasan_reject = fields.Text('Alasan Reject')
    
    @api.multi
    def reject_button(self):
        for loan in self:
            loan.loan_id.write({'alasan_reject': loan.alasan_reject})
            loan.loan_id.action_reject()
        # don't keep temporary notes in the database longer than necessary
        self.write({'alasan_reject': False})

class HREmployee(models.Model):
    _inherit = 'hr.employee'
    
    sisa_pinjaman = fields.Float(digits=dp.get_precision('Payroll'), string="Sisa Angsuran", compute='_compute_pinjaman')
    jumlah_pinjaman_x = fields.Integer(string="Pinjaman", compute='_compute_pinjaman')
    loan_ids = fields.One2many('hr.loan', 'employee_id')

    @api.one
    @api.depends('loan_ids.sisa_angsuran')
    def _compute_pinjaman(self):
#         sisa_pinjaman = 0.0
#         count = 0
#         for loan in self.env['hr.loan'].search([('employee_id','=',self.id)]):
#             sisa_pinjaman += loan.sisa_angsuran
#             count +=1
#         self.sisa_pinjaman = sisa_pinjaman
#         self.jumlah_pinjaman_x = count
        self.sisa_pinjaman = sum(loan.sisa_angsuran for loan in self.loan_ids if loan.state == 'approved')
        self.jumlah_pinjaman_x = self.loan_ids and len(self.loan_ids) or 0

class HRPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    loan_line_id = fields.Many2one('hr.loan.line', string='Loan Line')

    def get_inputs(self, cr, uid, contract_ids, date_from, date_to, context=None):
        res = super(HRPayslip, self).get_inputs(cr, uid, contract_ids, date_from, date_to, context=context)

        contract_obj = self.pool.get('hr.contract')
        employee_obj = self.pool.get('hr.employee')
        loan = self.pool.get('hr.loan')
        loan_line = self.pool.get('hr.loan.line')
        
        employee_id = contract_obj.browse(cr, uid, contract_ids, context=context)[0].employee_id.id
        employee = employee_obj.browse(cr, uid, employee_id, context=context)
        
        for result in res:
            if loan.get_condition(cr, uid, result.get('code'), context=context):
                loan_line_ids = loan_line.get_loan_line(cr, uid, employee, date_from, date_to, context=context)
                loan_ids = [x.loan_id.id for x in loan_line.browse(cr,uid,loan_line_ids)]
                if loan_ids:
                    result['amount'] = loan.get_amount(cr, uid, loan_ids, result['code'], context=context)
                if loan_line_ids:
                    result['amount'] = loan_line.get_amount(cr, uid, loan_line_ids, result['code'], context=context)

        return res

    def process_sheet(self, cr, uid, ids, context=None):
        loan_line_obj = self.pool.get('hr.loan.line')
        for payslip in self.browse(cr, uid, ids, context=context):
            if payslip.loan_line_id:
                loan_line_obj.write(cr, uid, [payslip.loan_line_id.id], {'paid': True}, context=context)
            
        return super(HRPayslip, self).process_sheet(cr, uid, ids, context=context)
    
    def onchange_employee_id(self, cr, uid, ids, date_from, date_to, employee_id=False, contract_id=False, context=None):
        employee_obj = self.pool.get('hr.employee')
        loan_obj = self.pool.get('hr.loan')
        loan_line_obj = self.pool.get('hr.loan.line')
        
        if context is None:
            context = {}
        res = super(HRPayslip, self).onchange_employee_id(cr, uid, ids, date_from, date_to, \
            employee_id=employee_id, contract_id=contract_id, context=context)

        if (not employee_id) or (not date_from) or (not date_to):
            return res
        
        employee_id = employee_obj.browse(cr, uid, employee_id, context=context)
        input_line_ids = res.get('value', {}) and res.get('value').get('input_line_ids', [])
        for input_line in input_line_ids:
            if loan_obj.get_condition(cr, uid, input_line.get('code'), context=context):
                loan_line_ids = loan_line_obj.get_loan_line(cr, uid, employee_id, date_from, date_to, context=context)
                if loan_line_ids:
                    loan_line = loan_line_obj.browse(cr, uid, loan_line_ids, context)
                    res['value']['loan_line_id'] = loan_line[0].id
                    input_line['amount'] = loan_line_obj.get_amount(cr, uid, loan_line_ids, input_line['code'], context=context)
        
        return res
    
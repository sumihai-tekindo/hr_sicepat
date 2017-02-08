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

class HRLoanType(models.Model):
    _name="hr.loan.type"
        
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', size=52, required=True)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('code', '=', name)] + args, limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()


class HRLoan(models.Model):
    # Private attributes
    _name = "hr.loan"
    _inherit = ['mail.thread']
    _description = 'HR Loan'
    _order = "tanggal desc, id desc"

    # Default methods
    

    # Fields declaration
    name = fields.Char(string='Number', readonly=True)
    loan_type = fields.Many2one('hr.loan.type', 'Loan Type', required=True, readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    tanggal = fields.Date(default=lambda self: fields.Date.context_today(self), readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    employee_id = fields.Many2one('hr.employee', 'Nama Karyawan', required=True, readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    jabatan_id = fields.Many2one('hr.job', string='Jabatan', compute='_get_employee', store=True, readonly=True)
    department_id = fields.Many2one('hr.department', string='Nama Cabang', compute='_get_employee', store=True, readonly=True)
    address_home_id = fields.Many2one(related='employee_id.address_home_id', readonly=True)
    pinjaman_unpaid = fields.Float(digits=dp.get_precision('Payroll'), string="Pinjaman Sebelumnya", compute='_compute_pinjaman_unpaid')
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
    notes = fields.Text(readonly=True, states={'draft': [('readonly', False)], 'submit': [('readonly', False)], 'reject': [('readonly', False)], 'approved': [('readonly', False)]})
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
        ('close','Closed'),
        ], string='Status', default='draft', track_visibility='onchange', copy=False,)
    availabiltiy = fields.Boolean(compute='_get_avail')
    
    # compute and search fields, in the same order that fields declaration
    @api.one
    @api.depends('employee_id')
    def _get_employee(self):
        self.jabatan_id = self.employee_id.job_id.id
        self.department_id = self.employee_id.department_id.id
        
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

    @api.one
    @api.depends('state','sisa_angsuran')
    def _get_avail(self):
        self.availabiltiy = False
        if self.state in ('approved', 'closed') and self.sisa_angsuran == 0.0:
            self.availabiltiy = True
            
    # Constraints and onchanges
    @api.multi
    def payment_method_change(self, payment_method):
        if payment_method and payment_method != 'bank':
            return {'value': {'bank_account_id': False}}

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
        
    @api.multi
    def action_close(self):
        self.state = 'close'
        
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


class HRLoanLine(models.Model):
    # Private attributes
    _name = "hr.loan.line"
    
    # Default methods
    

    # Fields declaration
    loan_id = fields.Many2one('hr.loan', string="Loan #", ondelete='cascade')
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
    @api.model
    def get_loan_line(self, employee, date_from, date_to, code):
        """
        @param employee: browse record of employee
        @param date_from: date field
        @param date_to: date field
        @return: returns the ids of all the salary structure lines for the given employee that need to be considered for the given dates
        """
        clause_1 = ['&',('tanggal_angsuran', '<=', date_to),('tanggal_angsuran','>=', date_from)]
        clause_final = [('loan_id.employee_id','=',employee.id), ('posted','=',True), ('paid','=',False), ('loan_id.loan_type.code','=',code)] + clause_1
        loan_line_ids = self.search(clause_final, order='tanggal_angsuran desc')
        return loan_line_ids

    @api.multi
    def get_amount(self):
        """
        @param code: char field
        @return: returns amount based on code
        """
        amount = 0.0
        for l in self:
            amount += l.nilai_angsuran
        return amount

    @api.model
    def get_condition(self, code):
        """
        @param code: char field
        @return: returns True or False
        """
        code_from_type = [t.code for t in self.env['hr.loan.type'].search([])]
        if code and code in code_from_type:
            return True
        return False

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
        
    loan_id = fields.Many2one('hr.loan', string='Loan', required=True, readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Nama Karyawan', required=True, readonly=True)
    loan_type = fields.Many2one('hr.loan.type', string='Loan Type', required=True, readonly=True)
    nilai_pinjaman = fields.Float(digits=dp.get_precision('Payroll'), string='Nilai Pinjaman', required=True, readonly=True)
    notes = fields.Text('Notes')
    
    @api.multi
    def close_button(self):
        for loan in self:
            loan.loan_id.write({'notes': loan.loan_id.notes + '\n' + loan.notes})
            loan.loan_id.action_close()
        # don't keep temporary notes in the database longer than necessary
        self.write({'notes': False})

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
    
    def get_inputs(self, cr, uid, contract_ids, date_from, date_to, context=None):
        result = super(HRPayslip, self).get_inputs(cr, uid, contract_ids, date_from, date_to, context=context)

        contract_obj = self.pool['hr.contract']
        employee_obj = self.pool['hr.employee']
        loan_line = self.pool['hr.loan.line']
        
        employee_id = contract_obj.browse(cr, uid, contract_ids, context=context)[0].employee_id.id
        employee = employee_obj.browse(cr, uid, employee_id, context=context)
        
        for res in result:
            if loan_line.get_condition(cr, uid, res.get('code'), context=context):
                loan_line_ids = loan_line.get_loan_line(cr, uid, employee, date_from, date_to, res['code'], context=context)
                if loan_line_ids:
                    res['amount'] = loan_line_ids.get_amount()
                    res['loan_line_ids'] = [(6, 0, [l.id for l in loan_line_ids])]

        return result

    def process_sheet(self, cr, uid, ids, context=None):
        loan_line_obj = self.pool['hr.loan.line']
        for payslip in self.browse(cr, uid, ids, context=context):
            for input in payslip.input_line_ids:
                if input.loan_line_ids:
                    for l in input.loan_line_ids:
                        loan_line_obj.write(cr, uid, [l.id], {'paid': True}, context=context)
        return super(HRPayslip, self).process_sheet(cr, uid, ids, context=context)

class HRPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'
    
    loan_line_ids = fields.Many2many('hr.loan.line', 'payslip_input_loan_line', 'payslip_input_id', 'loan_line_id', string='Loan Line')

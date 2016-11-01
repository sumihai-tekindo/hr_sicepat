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

from openerp import api, fields, models
from openerp.osv import osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class HROvertime(models.Model):
    _name = 'hr.overtime'
    
    name = fields.Char(string='Number', readonly=True)
    request_id = fields.Many2one('res.users', string='Requestor', readonly=True,
        default=lambda self: self.env.user)
    tanggal = fields.Date(default=lambda self: fields.Date.context_today(self), readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
#     department_id = fields.Many2one('hr.department', string='Nama Cabang', required=True, readonly=True,
#         states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    state = fields.Selection([
        ('draft','Open'),
        ('submit','Submit'),
        ('approved','Approved'),
        ('proses','Proses Di Gaji'),
        ('reject','Reject'),
        ], string='Status', default='draft')
    overtime_line = fields.One2many('hr.overtime.line', 'overtime_id', readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('hr.overtime')
        return super(HROvertime, self).create(vals)

    @api.multi
    def action_submit(self):
        self.state = 'submit'

    @api.multi
    def action_approve(self):
        status = False
        for line in self.overtime_line:
            if(line.state=='draft'):
                status=True
        if(status==False):
            self.state = 'approved'
        else:
            raise osv.except_osv(_('Gagal Di Proses'), _('silahkan lakukan Approve atau Reject setiap lemburan'))
        
    @api.multi
    def action_reject(self):
        status = False
        for line in self.overtime_line:
            if(line.state=='draft'):
                status=True
        if(status==False):
            self.state = 'reject'
        else:
            raise osv.except_osv(_('Gagal Di Proses'), _('silahkan lakukan Approve atau Reject setiap lemburan'))
        
    @api.multi
    def action_proses(self):
        self.state = 'proses'

# from .hr_salary_structure_amt import CODE2INPUT
# CODE2INPUT['OVERTIME']='nilai'
CODE2INPUT = {'OVERTIME': 'nilai'}

class HROvertimeLine(models.Model):
    _name = 'hr.overtime.line'
    _rec_name = 'overtime_id'
    
    overtime_id = fields.Many2one('hr.overtime', string='Overtime')
    employee_id = fields.Many2one('hr.employee', string='Nama Karyawan', required=True)
    jabatan_id = fields.Many2one('hr.job', string='Jabatan', related='employee_id.job_id', readonly=True)
    nilai = fields.Float(digits=dp.get_precision('Payroll'), string='Nilai Lemburan', required=True)
    alasan = fields.Text()
    state = fields.Selection([
        ('draft','Draft'),
        ('confirmed','Confirmed'),
        ('cancel','Cancel'),
        ], string='Status', default='draft')
    tanggal = fields.Date(related='overtime_id.tanggal', store=True)
#     department_id = fields.Many2one('hr.department', string='Nama Cabang', related='overtime_id.department_id')
    department_id = fields.Many2one('hr.department', string='Nama Cabang', readonly=True)
    overtime_state = fields.Selection(related='overtime_id.state', store=True, default='draft')
    
    @api.multi
    def action_confirm(self):
        self.state = 'confirmed'
        
    @api.multi
    def action_cancel(self):
        self.state = 'cancel'

    def get_overtime_line(self, cr, uid, employee, date_from, date_to, context=None):
        """
        @param employee: browse record of employee
        @param date_from: date field
        @param date_to: date field
        @return: returns the ids of all the salary structure lines for the given employee that need to be considered for the given dates
        """
        clause_1 = ['&',('tanggal', '<=', date_to),('tanggal','>=', date_from)]
        clause_final = [('employee_id','=',employee.id), ('state','=','confirmed'), ('overtime_state','=','proses')] + clause_1
        overtime_line_ids = self.search(cr, uid, clause_final, order='tanggal desc', context=context)
        return overtime_line_ids

    def get_amount(self, cr, uid, ids, code, context=None):
        """
        @param code: char field
        @return: returns amount based on code
        """
        overtime_line = self.browse(cr, uid, ids, context)
        return overtime_line[0][CODE2INPUT.get(code)]

    def get_condition(self, cr, uid, code, context=None):
        """
        @param code: char field
        @return: returns True or False
        """
        if code:
            if code in CODE2INPUT:
                return True
        return False
    
    @api.onchange('employee_id')
    def onchange_cabang_asal(self):
        if(self.employee_id):
            employee = self.env['hr.employee'].search([('id','=',self.employee_id.id)])
            self.department_id = employee.department_id.id
            self.jabatan_id = employee.job_id.id
            
    @api.model
    def create(self, vals):
        employee = self.env['hr.employee'].search([('id','=',vals['employee_id'])])
        vals['department_id'] = employee.department_id.id
        vals['jabatan_id'] = employee.job_id.id
        return super(HROvertimeLine, self).create(vals)
    
    @api.multi
    def write(self, vals):
        employee = self.env['hr.employee'].search([('id','=',vals.get('employee_id'))])
        if(employee):
            vals['department_id'] = employee.department_id.id
            vals['jabatan_id'] = employee.job_id.id
        return super(HROvertimeLine, self).write(vals)
    
class HRPayslip(models.Model):
    _inherit = 'hr.payslip'

    def get_inputs(self, cr, uid, contract_ids, date_from, date_to, context=None):
        res = super(HRPayslip, self).get_inputs(cr, uid, contract_ids, date_from, date_to, context=context)

        contract_obj = self.pool.get('hr.contract')
        employee_obj = self.pool.get('hr.employee')
        overtime_line = self.pool.get('hr.overtime.line')
        
        employee_id = contract_obj.browse(cr, uid, contract_ids, context=context)[0].employee_id.id
        employee = employee_obj.browse(cr, uid, employee_id, context=context)
        
        for result in res:
            if overtime_line.get_condition(cr, uid, result.get('code'), context=context):
                struct_line_ids = overtime_line.get_insentif_line(cr, uid, employee, date_from, date_to, context=context)
                if struct_line_ids:
                    result['amount'] = overtime_line.get_amount(cr, uid, struct_line_ids, result['code'], context=context)

        return res
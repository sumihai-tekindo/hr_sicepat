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
import openerp.addons.decimal_precision as dp

class HRInsentif(models.Model):
    _name = 'hr.insentif'
    
    name = fields.Char(string='Number', readonly=True)
    request_id = fields.Many2one('res.users', string='Requestor', readonly=True,
        default=lambda self: self.env.user)
    tanggal = fields.Date(default=lambda self: fields.Date.context_today(self), readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    nama_koordinator = fields.Many2one('hr.employee', string='Nama Koordinator Wilayah')
    state = fields.Selection([
        ('draft','Open'),
        ('submit','Submit'),
        ('reject','Reject'),
        ('approved','Approved'),
        ], string='State', readonly=True, default='draft')
    insentif_line = fields.One2many('hr.insentif.line', 'insentif_id', readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    
    @api.multi
    def action_submit(self):
        self.state = 'submit'

    @api.multi
    def action_approve(self):
        self.state = 'approved'
        
    @api.multi
    def action_reject(self):
        self.state = 'reject'

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('hr.insentif')
        return super(HRInsentif, self).create(vals)

# from .hr_salary_structure_amt import CODE2INPUT
# CODE2INPUT['INSENTIF']='nilai_insentif'
CODE2INPUT = {'INSENTIF': 'nilai_insentif'}

class HRInsentifLine(models.Model):
    _name = 'hr.insentif.line'
    _rec_name = 'insentif_id'

    insentif_id = fields.Many2one('hr.insentif', string='Insentif')
    employee_id = fields.Many2one('hr.employee', string='Nama Karyawan', required=True)
    jabatan_id = fields.Many2one('hr.job', string='Jabatan', readonly=True)
    nilai_insentif = fields.Float(digits=dp.get_precision('Payroll'), string='Nilai Insentif', required=True)
    alasan = fields.Text()
    tanggal = fields.Date(related='insentif_id.tanggal', store=True)
#     department_id = fields.Many2one('hr.department', string='Nama Cabang', related='insentif_id.department_id')
    department_id = fields.Many2one('hr.department', string='Nama Cabang', readonly=True)
    state = fields.Selection(related='insentif_id.state', store=True, default='draft')

    def get_insentif_line(self, cr, uid, employee, date_from, date_to, context=None):
        """
        @param employee: browse record of employee
        @param date_from: date field
        @param date_to: date field
        @return: returns the ids of all the salary structure lines for the given employee that need to be considered for the given dates
        """
        clause_1 = ['&',('tanggal', '<=', date_to),('tanggal','>=', date_from)]
        clause_final = [('employee_id','=',employee.id), ('state','=','approved')] + clause_1
        insentif_line_ids = self.search(cr, uid, clause_final, order='tanggal desc', context=context)
        return insentif_line_ids

    def get_amount(self, cr, uid, ids, code, context=None):
        """
        @param code: char field
        @return: returns amount based on code
        """
        insentif_line = self.browse(cr, uid, ids, context)
        return insentif_line[0][CODE2INPUT.get(code)]

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
        return super(HRInsentifLine, self).create(vals)
    
    @api.multi
    def write(self, vals):
        employee = self.env['hr.employee'].search([('id','=',vals.get('employee_id'))])
        if(employee):
            vals['department_id'] = employee.department_id.id
            vals['jabatan_id'] = employee.job_id.id
        return super(HRInsentifLine, self).write(vals)
    
class HRPayslip(models.Model):
    _inherit = 'hr.payslip'

    def get_inputs(self, cr, uid, contract_ids, date_from, date_to, context=None):
        res = super(HRPayslip, self).get_inputs(cr, uid, contract_ids, date_from, date_to, context=context)

        contract_obj = self.pool.get('hr.contract')
        employee_obj = self.pool.get('hr.employee')
        insentif_line = self.pool.get('hr.insentif.line')
        
        employee_id = contract_obj.browse(cr, uid, contract_ids, context=context)[0].employee_id.id
        employee = employee_obj.browse(cr, uid, employee_id, context=context)
        
        for result in res:
            if insentif_line.get_condition(cr, uid, result.get('code'), context=context):
                struct_line_ids = insentif_line.get_insentif_line(cr, uid, employee, date_from, date_to, context=context)
                if struct_line_ids:
                    result['amount'] = insentif_line.get_amount(cr, uid, struct_line_ids, result['code'], context=context)

        return res
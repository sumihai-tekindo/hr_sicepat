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
from openerp.exceptions import Warning
from openerp.osv import osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class HROvertime(models.Model):
    _name = 'hr.overtime'
    _order = "tanggal desc, id desc"
    
    name = fields.Char(string='Number', readonly=True)
    request_id = fields.Many2one('res.users', string='Requestor', readonly=True,
        default=lambda self: self.env.user)
    tanggal = fields.Date(default=lambda self: fields.Date.context_today(self), readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
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
        for line in self.overtime_line:
            if line.state not in ('confirmed', 'cancel'):
                raise Warning(_("Silahkan lakukan Approve atau Reject setiap lemburan."))
        self.state = 'approved'
        
    @api.multi
    def action_reject(self):
        for line in self.overtime_line:
            if line.state not in ('confirmed', 'cancel'):
                raise Warning(_("Silahkan lakukan Approve atau Reject setiap lemburan."))
        self.state = 'reject'
        
    @api.multi
    def action_proses(self):
        self.state = 'proses'


class HROvertimeLine(models.Model):
    _name = 'hr.overtime.line'
    _rec_name = 'employee_id'
    _order = 'tanggal desc, department_id, nilai desc'
    
    overtime_id = fields.Many2one('hr.overtime', string='Overtime', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Nama Karyawan', required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    jabatan_id = fields.Many2one('hr.job', string='Jabatan', compute='_get_employee', store=True, readonly=True)
    department_id = fields.Many2one('hr.department', string='Nama Cabang', compute='_get_employee', store=True, readonly=True)
    nilai = fields.Float(digits=dp.get_precision('Payroll'), string='Nilai Lemburan', required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    alasan = fields.Text(readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft','Draft'),
        ('confirmed','Confirmed'),
        ('cancel','Cancel'),
        ], string='Status', default='draft')
    tanggal = fields.Date(related='overtime_id.tanggal', store=True, readonly=True)
    overtime_state = fields.Selection(related='overtime_id.state', string='Status Overtime', store=True, default='draft', readonly=True)
    
    @api.multi
    def action_confirm(self):
        self.state = 'confirmed'
        
    @api.multi
    def action_cancel(self):
        self.state = 'cancel'

    @api.one
    @api.depends('employee_id')
    def _get_employee(self):
        self.jabatan_id = self.employee_id.job_id.id
        self.department_id = self.employee_id.department_id.id
            
    @api.model
    def get_overtime_line(self, contract, date_from, date_to):
        """
        @param contract: browse record of contract
        @param date_from: date field
        @param date_to: date field
        @return: returns the ids of all the salary structure lines for the given employee that need to be considered for the given dates
        """
        clause_1 = ['&',('tanggal', '<=', date_to),('tanggal','>=', date_from)]
        clause_final = [('employee_id','=',contract.employee_id.id), ('state','=','confirmed'), ('overtime_id.state','=','proses')] + clause_1
        overtime_line_ids = self.search(clause_final, order='tanggal desc')
        return overtime_line_ids


class HRPayslip(models.Model):
    _inherit = 'hr.payslip'

    def get_inputs(self, cr, uid, contract_ids, date_from, date_to, context=None):
        res = super(HRPayslip, self).get_inputs(cr, uid, contract_ids, date_from, date_to, context=context)

        contract_obj = self.pool.get('hr.contract')
        overtime_line = self.pool.get('hr.overtime.line')
        
        for result in res:
            if result.get('code') == 'OVERTIME':
                contract = contract_obj.browse(cr, uid, [result['contract_id']], context=context)
                struct_line_ids = overtime_line.get_overtime_line(cr, uid, contract, date_from, date_to, context=context)
                if struct_line_ids:
                    result['amount'] = struct_line_ids[0].nilai

        return res
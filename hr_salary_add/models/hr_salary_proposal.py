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
from openerp import models, fields, api, _
from openerp.exceptions import AccessError, Warning

# 3 :  imports from odoo modules
import openerp.addons.decimal_precision as dp


class HRSalaryProposal(models.Model):
    # Private attributes
    _name = "hr.salary.proposal"
    
    # Default methods
    

    # Fields declaration
    name = fields.Char(string='Number', readonly=True)
    tanggal = fields.Date(default=lambda self: fields.Date.context_today(self), readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    requestor = fields.Many2one('res.users', string="Requestor", default=lambda self: self.env.user, readonly=True)
    nama_cabang = fields.Many2one('hr.department', string="Nama Cabang", readonly=True)
    nama_karyawan = fields.Many2one("hr.employee", string="Nama Karyawan", required=True, readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    jabatan = fields.Many2one('hr.job', string="Jabatan", readonly=True)
    contract_id = fields.Many2one('hr.contract', string='Contract')
    wage = fields.Float(string='Wage', digits=dp.get_precision('Payroll'))
    gaji_semula = fields.Float(digits=dp.get_precision('Payroll'), string="Gaji Awal", compute="compute_gaji", readonly=True)
    kenaikan_gaji = fields.Float(digits=dp.get_precision('Payroll'), string="Kenaikan Gaji", required=True, readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    gaji_usulan = fields.Float(digits=dp.get_precision('Payroll'), string="Gaji Usulan", compute="compute_gaji", readonly=True)
    alasan = fields.Text(readonly=True, states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    state = fields.Selection([
        ('draft','Open'),
        ('submit','Submit'),
        ('reject','Reject'),
        ('approved','Approved'),
        ], string='Status', default='draft', track_visibility='onchange', copy=False,)
    
    # compute and search fields, in the same order that fields declaration
    @api.one
    @api.depends('wage','kenaikan_gaji')
    def compute_gaji(self):
#         if((self.gaji_semula!=0) and (self.kenaikan_gaji!=0)):
#             self.gaji_usulan = self.gaji_semula+self.kenaikan_gaji
        self.gaji_semula = self.wage
        self.gaji_usulan = self.gaji_semula + self.kenaikan_gaji
            
    # Constraints and onchanges
    @api.one
    @api.constrains('contract_id')
    def _check_contract(self):
        if not self.contract_id:
            raise Warning(_('Karyawan tidak mempunyai kontrak kerja! Silakan buat kontrak kerja.'))
        
    @api.onchange('nama_karyawan','tanggal')
    def onchange_karyawan(self):
        if self.nama_karyawan:
            self.nama_cabang = self.nama_karyawan.department_id and self.nama_karyawan.department_id.id or False
            self.jabatan = self.nama_karyawan.job_id and self.nama_karyawan.job_id.id or False
            contract_ids = self.env['hr.payslip'].get_contract(self.nama_karyawan, self.tanggal, self.tanggal)
            if not contract_ids:
                self.contract_id = False
                self.wage = 0.0
                return
            contract = self.env['hr.contract'].browse(contract_ids[0])
            self.contract_id = contract and contract.id or False
            self.wage = contract and contract.wage or 0.0
            
    # CRUD methods
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get("salary.proposal")
        employee = self.env['hr.employee'].search([('id','=',vals['nama_karyawan'])])
        vals['nama_cabang'] = employee.department_id and employee.department_id.id or False
        vals['jabatan'] = employee.job_id and employee.job_id.id or False
        return super(HRSalaryProposal, self).create(vals)
    
    @api.multi
    def write(self, vals):
        if vals.get('nama_karyawan'):
            employee = self.env['hr.employee'].search([('id','=',vals.get('nama_karyawan'))])
            vals['nama_cabang'] = employee.department_id and employee.department_id.id or False
            vals['jabatan'] = employee.job_id and employee.job_id.id or False
        return super(HRSalaryProposal, self).write(vals)

    # Action methods
    @api.multi
    def action_submit(self):
        self.state = 'submit'

    @api.multi
    def action_approve(self):
        self.contract_id.wage = self.gaji_usulan
        self.state = 'approved'
        
    @api.multi
    def action_reject(self):
        self.state = 'reject'
        
    # Business methods

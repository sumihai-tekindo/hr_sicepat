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


class hr_promotion(models.Model):
    # Private attributes
    _name = "hr.promotion"
    
    # Default methods
    

    # Fields declaration
    name = fields.Char(string="code", default=lambda self: self.env['ir.sequence'].get("promotion"))
    tanggal = fields.Date(default=lambda self: fields.Date.context_today(self))
    requestor = fields.Many2one('res.users', string="Requestor", default=lambda self: self.env.user)
    nama_karyawan = fields.Many2one("hr.employee", string="Nama Karyawan", required=True)
    jabatan_awal = fields.Many2one('hr.job', string="Jabatan Semula", readonly=True)
    cabang_awal = fields.Many2one('hr.department', string="Cabang Asal", readonly=True)
    usulan_jabatan_baru = fields.Many2one('hr.job', string="Usulan Jabatan", required=True)
    cabang_baru = fields.Many2one('hr.department', string="Cabang Baru", required=True)
    state = fields.Selection([
        ('open','Open'),
        ('submit','Submit'),
        ('reject','Reject'),
        ('approved','Approved'),
        ], string='Status', default='open')
    
    # compute and search fields, in the same order that fields declaration


    # Constraints and onchanges
    @api.onchange('nama_karyawan')
    def onchange_cabang_asal(self):
        if self.nama_karyawan:
#             employee = self.env['hr.employee'].search([('id','=',self.nama_karyawan.id)])
#             self.cabang_awal = employee.department_id.id
#             self.jabatan_awal = employee.job_id.id
            self.cabang_awal = self.nama_karyawan.department_id and self.nama_karyawan.department_id.id or False
            self.jabatan_awal = self.nama_karyawan.job_id and self.nama_karyawan.job_id.id or False
            
    # CRUD methods
    @api.model
    def create(self, vals):
        employee = self.env['hr.employee'].search([('id','=',vals['nama_karyawan'])])
        vals['cabang_awal'] = employee.department_id and employee.department_id.id or False
        vals['jabatan_awal'] = employee.job_id and employee.job_id.id or False
        return super(hr_promotion, self).create(vals)
    
    @api.multi
    def write(self, vals):
#         employee = self.env['hr.employee'].search([('id','=',vals.get('nama_karyawan'))])
#         if(employee):
#             vals['cabang_awal'] = employee.department_id.id
#             vals['jabatan_awal'] = employee.job_id.id
        if vals.get('nama_karyawan'):
            employee = self.env['hr.employee'].search([('id','=',vals.get('nama_karyawan'))])
            vals['nama_cabang'] = employee.department_id and employee.department_id.id or False
            vals['jabatan'] = employee.job_id and employee.job_id.id or False
        return super(hr_promotion, self).write(vals)

    # Action methods
    @api.multi
    def action_submit(self):
        self.state = 'submit'

    @api.multi
    def action_approve(self):
        self.nama_karyawan.department_id = self.cabang_baru.id
        self.nama_karyawan.job_id = self.usulan_jabatan_baru.id
        self.state = 'approved'
#         employee = self.env['hr.employee'].search([('id','=',self.nama_karyawan.id)])
#         employee.write({'department_id':self.cabang_baru.id})
#         employee.write({'job_id':self.usulan_jabatan_baru.id})
        
    @api.multi
    def action_reject(self):
        self.state = 'reject'
        
    # Business methods

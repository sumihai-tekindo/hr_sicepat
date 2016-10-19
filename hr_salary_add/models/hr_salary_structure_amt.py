# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Pambudi Satria (<https://github.com/pambudisatria>).
#    @author Pambudi Satria <pambudi.satria@yahoo.com>
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

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp

class SalaryStructure(models.Model):
    _name = "hr.salary.structure"
    
    name = fields.Char(string="Number", readonly=True)
    request_id = fields.Many2one('res.users', string="Requestor", readonly=True,
        default=lambda self: self.env.user)
    tanggal = fields.Date(default=lambda self: fields.Date.context_today(self), readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    dept_id = fields.Many2one('hr.department', string="Nama Cabang", required=True, readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    state = fields.Selection([
        ('draft','Open'),
        ('submit','Submit'),
        ('reject','Reject'),
        ('approved','Approved'),
        ], string='State', readonly=True, default='draft')
    structure_line = fields.One2many('salary.structure.line', 'structure_id', readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    
    @api.multi
    def action_submit(self):
        self.state = 'submit'
#         for line in self.structure_line:
#             line.state = 'submit'

    @api.multi
    def action_approve(self):
        self.state = 'approved'
#         for line in self.structure_line:
#             line.state = 'approved'
        
    @api.multi
    def action_reject(self):
        self.state = 'reject'
#         for line in self.structure_line:
#             line.state = 'reject'

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get("salary.structure.amt")
        return super(SalaryStructure, self).create(vals)


class SalaryStructureLine(models.Model):
    _name = "salary.structure.line"

    structure_id = fields.Many2one('hr.salary.structure', string='Salary Structure')
    jabatan_id = fields.Many2one('hr.job', string="Jabatan", required=True)
    uang_makan = fields.Float(digits=dp.get_precision('Payroll'), string="Uang Makan")
    transport = fields.Float(digits=dp.get_precision('Payroll'), string="Transport")
    uang_kerajinan = fields.Float(digits=dp.get_precision('Payroll'), string="Uang Kerajinan")
    tunj_operasional = fields.Float(digits=dp.get_precision('Payroll'), string="Tunjangan Operasional")
    tunj_jabatan = fields.Float(digits=dp.get_precision('Payroll'), string="Tunjangan Jabatan")
    service_motor = fields.Float(digits=dp.get_precision('Payroll'), string="Service Motor")
    tanggal = fields.Date(related='structure_id.tanggal')
    dept_id = fields.Many2one('hr.department', string="Nama Cabang", related='structure_id.dept_id')
    state = fields.Selection(related='structure_id.state', store=True, default='draft')

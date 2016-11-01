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

class DeliveryPackage(models.Model):
    # Private attributes
    _name = "delivery.package.target"
    
    # Default methods


    # Fields declaration
    name = fields.Char('Number', readonly=True)
    date_start = fields.Date('Tanggal mulai', required=True, readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    date_end = fields.Date('Tanggal akhir', required=True, readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    department_id = fields.Many2one('hr.department', string='Nama Cabang', required=True, readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    target_paket = fields.Integer(required=True, readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    nilai_target = fields.Float(digits=dp.get_precision('Payroll'), string='Nilai Target', required=True, readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    target_paket_bulan_lalu = fields.Integer(compute='compute_target_bulan_lalu', readonly=True)
    pertambahan_bonus = fields.Integer(required=True, readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    nilai_bonus = fields.Float(digits=dp.get_precision('Payroll'), string='Nilai Bonus', required=True, readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    pertambahan_bonus_bulan_lalu = fields.Integer(compute='compute_target_bulan_lalu', readonly=True)
    state = fields.Selection([
            ('draft','Open'),
            ('submit','Submit'),
            ('reject','Reject'),
            ('approved','Approved'),
        ], string='Status', default='draft')
    
    # compute and search fields, in the same order that fields declaration
    @api.one
    @api.depends('department_id','date_start','date_end')
    def compute_target_bulan_lalu(self):
        clause_1 = ['&',('date_end', '<', self.date_end),('date_end','<', self.date_start)]
        #OR if it starts between the given dates
        clause_2 = ['&',('date_start', '<', self.date_end),('date_start','<', self.date_start)]
        #OR if it starts before the date_from and finish after the date_end (or never finish)
        clause_3 = ['&',('date_start','<', self.date_start),'|',('date_end', '=', False),('date_end','<', self.date_end)]
        clause_final =  [('department_id', '=', self.department_id.id),('state','=','approved'),'|','|'] + clause_1 + clause_2 + clause_3
        delivery_ids = self.search(clause_final, order='date_end desc')
        if delivery_ids:
            self.target_paket_bulan_lalu = delivery_ids[0].target_paket
            self.pertambahan_bonus_bulan_lalu = delivery_ids[0].pertambahan_bonus
            
    # Constraints and onchanges
    @api.one
    @api.constrains('date_start','date_end','department_id','state')
    def _check_date(self):
        for package_target in self:
            if package_target.state != 'approved':
                continue
            where = []
            if package_target.date_start:
                where.append("((date_end>='%s') or (date_end is null))" % (package_target.date_start,))
            if package_target.date_end:
                where.append("((date_start<='%s') or (date_start is null))" % (package_target.date_end,))

            self._cr.execute('SELECT id ' \
                    'FROM delivery_package_target ' \
                    'WHERE '+' and '.join(where) + (where and ' and ' or '')+
                        'department_id=%s ' \
                        'AND state=%s ' \
                        'AND id <> %s', (
                            package_target.department_id.id,
                            'approved',
                            package_target.id))
            if self._cr.fetchall():
                raise Warning(_('You cannot have 2 package target that overlap for each department!'))
        return True

    # CRUD methods
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('delivery.package')
        return super(DeliveryPackage, self).create(vals)

    # Action methods
    @api.multi
    def action_submit(self):
        self.state = 'submit'

    @api.multi
    def action_approve(self):
        self.state = 'approved'
        
    @api.multi
    def action_reject(self):
        self.state = 'reject'
        
    # Business methods
    def get_target(self, cr, uid, employee, date_from, date_to, context=None):
        """
        @param employee: browse record of employee
        @param date_from: date field
        @param date_to: date field
        @return: returns the ids of all the delivery target for the given employee that need to be considered for the given dates
        """
        #a contract is valid if it ends between the given dates
        clause_1 = ['&',('date_end', '<=', date_to),('date_end','>=', date_from)]
        #OR if it starts between the given dates
        clause_2 = ['&',('date_start', '<=', date_to),('date_start','>=', date_from)]
        #OR if it starts before the date_from and finish after the date_end (or never finish)
        clause_3 = ['&',('date_start','<=', date_from),'|',('date_end', '=', False),('date_end','>=', date_to)]
        clause_final =  [('department_id', '=', employee.department_id.id),'|',('state','=','approved'),'|'] + clause_1 + clause_2 + clause_3
        target_ids = self.search(cr, uid, clause_final, context=context)
        return target_ids


class DeliveryPackageRun(models.Model):
    _name = "delivery.package.run"
    _rec_name = 'employee_id'
    
    employee_id = fields.Many2one('hr.employee', 'Karyawan', required=True)
    date_delivery = fields.Date('Tanggal pengiriman', required=True)
    department_id = fields.Many2one('hr.department', string='Nama Cabang', related='employee_id.department_id', readonly=True)
    total_paket = fields.Integer(required=True)

    def get_delivery(self, cr, uid, employee, date_from, date_to, context=None):
        """
        @param employee: browse record of employee
        @param date_from: date field
        @param date_to: date field
        @return: returns total delivery for the given employee that need to be considered for the given dates
        """
        total_delivery = 0
        #a contract is valid if it ends between the given dates
        clause_1 = ['&',('date_delivery', '<=', date_to),('date_delivery','>=', date_from)]
        clause_final =  [('employee_id', '=', employee.id)] + clause_1
        delivery_ids = self.search(cr, uid, clause_final, context=context)
        if delivery_ids:
            for delivery in self.browse(cr, uid, delivery_ids):
                total_delivery += delivery.total_paket 
        return total_delivery

class HRPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    total_paket = fields.Integer()
    target_paket = fields.Integer()
    nilai_target = fields.Float(digits=dp.get_precision('Payroll'), string='Nilai Target')
    pertambahan_bonus = fields.Integer()
    nilai_bonus = fields.Float(digits=dp.get_precision('Payroll'), string='Nilai Bonus')
     
    def get_inputs(self, cr, uid, contract_ids, date_from, date_to, context=None):
        contract_obj = self.pool.get('hr.contract')

        res = super(HRPayslip, self).get_inputs(cr, uid, contract_ids, date_from, date_to, context=context)
 
        contract = contract_obj.browse(cr, uid, contract_ids, context=context)[0]
        clause = [('employee_id','=', contract.employee_id.id), ('contract_id','=', contract.id), ('date_from','=',date_from), ('date_to','=',date_to)]
        current_id = self.search(cr, uid, clause, limit=1, context=context)
        
        if not current_id:
            return res
        
        current_obj = self.browse(cr, uid, current_id, context)
         
        for result in res:
            if result.get('code') in ('TARGET', 'TBONUS'):
                if result['code'] == 'TARGET':
                    result['amount'] = current_obj.target_paket * current_obj.nilai_target
                if result['code'] == 'TBONUS':
                    result['amount'] = int((current_obj.total_paket - current_obj.target_paket) / current_obj.pertambahan_bonus) * current_obj.nilai_bonus
 
        return res

    def onchange_employee_id(self, cr, uid, ids, date_from, date_to, employee_id=False, contract_id=False, context=None):
        employee_obj = self.pool.get('hr.employee')
        target_obj = self.pool.get('delivery.package.target')
        delivery_obj = self.pool.get('delivery.package.run')
        
        if context is None:
            context = {}
            
        res = super(HRPayslip, self).onchange_employee_id(cr, uid, ids, date_from=date_from, date_to=date_to, \
            employee_id=employee_id, contract_id=contract_id, context=context)

        if (not employee_id) or (not date_from) or (not date_to):
            return res
        
        employee_id = employee_obj.browse(cr, uid, employee_id, context=context)
        target_ids = target_obj.get_target(cr, uid, employee_id, date_from, date_to, context=context)
        if not target_ids:
            return res
        
        target = target_obj.browse(cr, uid, target_ids[0], context=context)
        res['value']['target_paket'] = target.target_paket
        res['value']['nilai_target'] = target.nilai_target
        res['value']['pertambahan_bonus'] = target.pertambahan_bonus
        res['value']['nilai_bonus'] = target.nilai_bonus
        res['value']['total_paket'] = delivery_obj.get_delivery(cr, uid, employee_id, date_from, date_to, context=context)
        return res

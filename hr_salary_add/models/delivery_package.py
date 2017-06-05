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
from openerp.exceptions import ValidationError, Warning
from openerp.tools.safe_eval import safe_eval as eval

# 3 :  imports from odoo modules
import openerp.addons.decimal_precision as dp

class DeliveryPackageZone(models.Model):
    _name = "delivery.package.zone"
    
    name = fields.Char('Zone Name', required=True)

    
class DeliveryPackage(models.Model):
    # Private attributes
    _name = "delivery.package.target"
    _order = "date_end desc, id desc"
    
    # Default methods


    # Fields declaration
    name = fields.Char('Number', readonly=True)
    date_start = fields.Date('Tanggal mulai', required=True, readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    date_end = fields.Date('Tanggal akhir', required=True, readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    department_id = fields.Many2one('hr.department', string='Nama Cabang', required=True, readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
#     target_paket = fields.Integer(string='Target Paket', readonly=True,
#         states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
#     nilai_target = fields.Float(digits=dp.get_precision('Payroll'), string='Nilai Target', readonly=True,
#         states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
#     target_paket_bulan_lalu = fields.Integer(string="Target Bulan Lalu", compute='compute_target_bulan_lalu', readonly=True)
#     pertambahan_bonus = fields.Integer(string='Pertambahan Bonus', readonly=True,
#         states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
#     nilai_bonus = fields.Float(digits=dp.get_precision('Payroll'), string='Nilai Bonus', readonly=True,
#         states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
#     pertambahan_bonus_bulan_lalu = fields.Integer(string="Bonus Bulan Lalu", compute='compute_target_bulan_lalu', readonly=True)
#     target_manual = fields.Boolean(string='Manual Calculation ?', default=True)
    target_condition_select = fields.Selection([('none', 'Always True'),('python', 'Python Expression')], "Condition Based on", default='none')
    target_condition_python = fields.Text('Python Condition', help='Applied this for calculation if condition is true. You can specify condition like total_consigment > 1000.',
        default='''
# Available variables:
#----------------------
# employee: hr.employee object
# contract: hr.contract object
# total_consignment: total of consignment delivered
# total_courier: total of courier

# Note: returned value have to be set in the variable 'result'

result = total_consignment > 1500''')
    target_amount_select = fields.Selection([
        ('fix','Fixed Amount'),
        ('code','Python Code'),
    ],'Amount Type', select=True, help="The computation method for the target amount.", default='fix')
    target_quantity = fields.Char('Quantity', help="It is used in computation for percentage and fixed amount." \
        "For e.g. A target having fixed amount of Rp 500 per target can have its quantity defined in expression like total_consigment.", default="1.0")
    target_amount_fix = fields.Float('Fixed Amount', digits=dp.get_precision('Payroll'), default=0.0)
    target_amount_python_compute = fields.Text('Python Code', default='''
# Available variables:
#----------------------
# employee: hr.employee object
# contract: hr.contract object
# total_consignment: total of consignment delivered
# total_courier: total of courier

# Note: returned value have to be set in the variable 'result'

result = total_consignment * 500''')
#     bonus_manual = fields.Boolean(string='Manual Calculation ?', default=True)
    bonus_condition_select = fields.Selection([('none', 'Always True'),('python', 'Python Expression')], "Condition Based on", default='none')
    bonus_condition_python = fields.Text('Python Condition', help='Applied this for calculation if condition is true. You can specify condition like total_consigment > 1000.',
        default='''
# Available variables:
#----------------------
# employee: hr.employee object
# contract: hr.contract object
# total_consignment: total of consignment delivered
# total_courier: total of courier

# Note: returned value have to be set in the variable 'result'

result = total_consignment > 1500''')
    bonus_amount_select = fields.Selection([
        ('fix','Fixed Amount'),
        ('code','Python Code'),
    ],'Amount Type', select=True, help="The computation method for the target amount.", default='fix')
    bonus_quantity = fields.Char('Quantity', help="It is used in computation for percentage and fixed amount." \
        "For e.g. A target having fixed amount of Rp 500 per target can have its quantity defined in expression like total_consigment.", default="1.0")
    bonus_amount_fix = fields.Float('Fixed Amount', digits=dp.get_precision('Payroll'), default=0.0)
    bonus_amount_python_compute = fields.Text('Python Code', default='''
# Available variables:
#----------------------
# employee: hr.employee object
# contract: hr.contract object
# total_consignment: total of consignment delivered
# total_courier: total of courier

# Note: returned value have to be set in the variable 'result'

result = total_consignment * 500''')
    state = fields.Selection([
            ('draft','Open'),
            ('submit','Submit'),
            ('reject','Reject'),
            ('approved','Approved'),
        ], string='Status', default='draft')
    zone_id = fields.Many2one('delivery.package.zone', 'Zone ID', readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    
    # compute and search fields, in the same order that fields declaration
    @api.one
    @api.depends('department_id','date_start','date_end','zone_id')
    def compute_target_bulan_lalu(self):
        clause_1 = ['&',('date_end', '<', self.date_end),('date_end','<', self.date_start)]
        #OR if it starts between the given dates
        clause_2 = ['&',('date_start', '<', self.date_end),('date_start','<', self.date_start)]
        #OR if it starts before the date_from and finish after the date_end (or never finish)
        clause_3 = ['&',('date_start','<', self.date_start),'|',('date_end', '=', False),('date_end','<', self.date_end)]
        clause_final =  [('department_id', '=', self.department_id.id),self.zone_id and ('zone_id', '=', self.zone_id.id) or ('zone_id', '=', False),('state','=','approved'),'|','|'] + clause_1 + clause_2 + clause_3
        delivery_ids = self.search(clause_final, order='date_end desc')
        if delivery_ids:
            self.target_paket_bulan_lalu = delivery_ids[0].target_paket
            self.pertambahan_bonus_bulan_lalu = delivery_ids[0].pertambahan_bonus
            
    # Constraints and onchanges
    @api.one
    @api.constrains('date_start','date_end','department_id','state','zone_id')
    def _check_constraint_target(self):
        for package_target in self:
            if package_target.state != 'approved':
                continue
            where = []
            where.append(package_target.zone_id and "(zone_id=%s)" % (package_target.zone_id.id,) or "(zone_id is null)")
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
    @api.model
    def get_target(self, employee, date_from, date_to):
        """
        @param employee: browse record of employee
        @param date_from: date field
        @param date_to: date field
        @return: returns records of the delivery target for the given employee that need to be considered for the given dates
        """
        #a delivery target is valid if it ends between the given dates
        clause_1 = ['&',('date_end', '<=', date_to),('date_end','>=', date_from)]
        #OR if it starts between the given dates
        clause_2 = ['&',('date_start', '<=', date_to),('date_start','>=', date_from)]
        #OR if it starts before the date_from and finish after the date_end (or never finish)
        clause_3 = ['&',('date_start','<=', date_from),'|',('date_end', '=', False),('date_end','>=', date_to)]
        clause_final =  [('department_id', '=', employee.department_id.id), employee.zone_id and ('zone_id', '=', employee.zone_id.id) or ('zone_id', '=', False),'|',('state','=','approved'),'|'] + clause_1 + clause_2 + clause_3
        target = self.search(clause_final, order='date_end desc', limit=1)
        return target

    @api.multi
    def compute_target(self, localdict):
        """
        :param localdict: dictionary containing the environment in which to compute the target
        :return: returns a tuple build as the base/amount computed and the quantity
        :rtype: (float, float)
        """
        self.ensure_one()
        if self.target_amount_select == 'fix':
            try:
                return self.target_amount_fix, float(eval(self.target_quantity, localdict))
            except:
                raise ValidationError(_('Wrong quantity defined for target %s (%s - %s).')% (self.name, self.date_start, self.date_end))
        elif self.target_amount_select == 'code':
            try:
                eval(self.target_amount_python_compute, localdict, mode='exec', nocopy=True)
                return float(localdict['result']), 'result_qty' in localdict and localdict['result_qty'] or 1.0
            except:
                raise ValidationError(_('Wrong python code defined for target %s (%s - %s).')% (self.name, self.date_start, self.date_end))

    @api.multi
    def compute_bonus(self, localdict):
        """
        :param localdict: dictionary containing the environment in which to compute the bonus
        :return: returns a tuple build as the base/amount computed and the quantity
        :rtype: (float, float)
        """
        self.ensure_one()
        if self.bonus_amount_select == 'fix':
            try:
                return self.bonus_amount_fix, float(eval(self.bonus_quantity, localdict))
            except:
                raise ValidationError(_('Wrong quantity defined for target %s (%s - %s).')% (self.name, self.date_start, self.date_end))
        elif self.bonus_amount_select == 'code':
            try:
                eval(self.bonus_amount_python_compute, localdict, mode='exec', nocopy=True)
                return float(localdict['result']), 'result_qty' in localdict and localdict['result_qty'] or 1.0
            except:
                raise ValidationError(_('Wrong python code defined for target %s (%s - %s).')% (self.name, self.date_start, self.date_end))

    @api.multi
    def target_condition(self, localdict):
        """
        :param localdict: dictionary containing the environment in which to compute the target
        @return: returns True if the given rule match the condition for the given localdict. Return False otherwise.
        """
        self.ensure_one()

        if self.target_condition_select == 'none':
            return True
        elif self.target_condition_select == 'python':
            try:
                eval(self.target_condition_python, localdict, mode='exec', nocopy=True)
                return 'result' in localdict and localdict['result'] or False
            except:
                raise ValidationError(_('Wrong python condition defined for target %s (%s - %s).')% (self.name, self.date_start, self.date_end))

    @api.multi
    def bonus_condition(self, localdict):
        """
        :param localdict: dictionary containing the environment in which to compute the bonus
        @return: returns True if the given rule match the condition for the given localdict. Return False otherwise.
        """
        self.ensure_one()

        if self.bonus_condition_select == 'none':
            return True
        elif self.bonus_condition_select == 'python':
            try:
                eval(self.bonus_condition_python, localdict, mode='exec', nocopy=True)
                return 'result' in localdict and localdict['result'] or False
            except:
                raise ValidationError(_('Wrong python condition defined for target %s (%s - %s).')% (self.name, self.date_start, self.date_end))


class DeliveryPackageRun(models.Model):
    _name = "delivery.package.run"
    _rec_name = 'employee_id'
    _order = "date_delivery desc, department_id, total_paket desc"
    
    employee_id = fields.Many2one('hr.employee', 'Karyawan', required=True)
    date_delivery = fields.Date('Tanggal pengiriman', required=True)
    department_id = fields.Many2one('hr.department', string='Nama Cabang', compute='_get_employee', store=True, readonly=True)
    total_paket = fields.Integer(required=True)

    @api.one
    @api.depends('employee_id')
    def _get_employee(self):
        self.department_id = self.employee_id.department_id.id
        
    @api.model
    def get_delivery(self, employee, date_from, date_to):
        """
        @param employee: browse record of employee
        @param date_from: date field
        @param date_to: date field
        @return: returns total delivery for the given employee that need to be considered for the given dates
        """
        total_delivery = 0
        #a contract is valid if it ends between the given dates
        clause_1 = ['&',('date_delivery', '<=', date_to),('date_delivery','>=', date_from)]
        clause_final = [('employee_id', '=', employee.id)] + clause_1
        if employee.as_head:
            clause_final = [('department_id', '=', employee.department_id.id), ('employee_id', '!=', employee.id)] + clause_1
        delivery_ids = self.search(clause_final)
        if delivery_ids:
            for delivery in delivery_ids:
                if employee.as_head:
                    target = self.env['delivery.package.target'].get_target(delivery.employee_id, date_from, date_to)
                    target_paket = target and target[0].target_paket or 0
                    target = self.env['delivery.package.target'].get_target(employee, date_from, date_to)
                    pertambahan_bonus = target and target[0].pertambahan_bonus or 0
                    try:
                        t_bonus = int(((delivery.total_paket - target_paket) > 0 and (delivery.total_paket - target_paket) or 0) / pertambahan_bonus)
                    except:
                        t_bonus = 0
                    total_delivery += t_bonus * pertambahan_bonus
                else:
                    total_delivery += delivery.total_paket
        return total_delivery

    @api.model
    def get_deliveries(self, employee, date_from, date_to):
        """
        @param employee: browse record of employee
        @param date_from: date field
        @param date_to: date field
        @return: returns delivery records for the given employee that need to be considered for the given dates
        """
        clause_1 = ['&',('date_delivery', '<=', date_to),('date_delivery','>=', date_from)]
        clause_final = [('employee_id', '=', employee.id)] + clause_1
        if employee.as_head:
            clause_final = [('department_id', '=', employee.department_id.id), ('employee_id', '!=', employee.id)] + clause_1
        deliveries = self.search(clause_final, order='employee_id, date_delivery')
        return deliveries

    @api.multi
    def get_total_consignment(self):
        total_paket = 0
        for delivery in self:
            total_paket += delivery.total_paket
        return total_paket

    @api.multi
    def get_total_courier(self):
        delivery_dict = {}
        for delivery in self:
            key = delivery.employee_id.id
            if delivery_dict.get(key):
                delivery_dict[key]['lines'] += delivery
                delivery_dict[key]['total_paket'] += delivery.total_paket
            else:
                delivery_dict[key] = {
                        'lines': delivery,
                        'total_paket': delivery.total_paket,
                    }
        return len(delivery_dict)


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    as_head = fields.Boolean('As Head')
    zone_id = fields.Many2one('delivery.package.zone', 'Zone ID')


class HRPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    total_paket = fields.Integer()
    target_paket = fields.Integer()
    nilai_target = fields.Float(digits=dp.get_precision('Payroll'), string='Nilai Target')
    pertambahan_bonus = fields.Integer()
    nilai_bonus = fields.Float(digits=dp.get_precision('Payroll'), string='Nilai Bonus')
     
#     def get_inputs(self, cr, uid, contract_ids, date_from, date_to, context=None):
#         contract_obj = self.pool.get('hr.contract')
# 
#         res = super(HRPayslip, self).get_inputs(cr, uid, contract_ids, date_from, date_to, context=context)
#  
#         contract = contract_obj.browse(cr, uid, contract_ids, context=context)[0]
#         clause = [('employee_id','=', contract.employee_id.id), ('contract_id','=', contract.id), ('date_from','=',date_from), ('date_to','=',date_to)]
#         current_id = self.search(cr, uid, clause, limit=1, context=context)
#         
#         if not current_id:
#             return res
#         
#         current_obj = self.browse(cr, uid, current_id, context)
#          
#         for result in res:
#             if result.get('code') in ('TARGET', 'TBONUS'):
#                 if result['code'] == 'TARGET':
#                     result['amount'] = current_obj.target_paket * current_obj.nilai_target
#                 if result['code'] == 'TBONUS':
#                     result['amount'] = int((current_obj.total_paket - current_obj.target_paket) / current_obj.pertambahan_bonus) * current_obj.nilai_bonus
#  
#         return res
# 
#     def onchange_employee_id(self, cr, uid, ids, date_from, date_to, employee_id=False, contract_id=False, context=None):
#         employee_obj = self.pool.get('hr.employee')
#         target_obj = self.pool.get('delivery.package.target')
#         delivery_obj = self.pool.get('delivery.package.run')
#         
#         if context is None:
#             context = {}
# 
#         res = super(HRPayslip, self).onchange_employee_id(cr, uid, ids, date_from, date_to, employee_id=employee_id, contract_id=contract_id, context=context)
# 
# 
#         if (not employee_id) or (not date_from) or (not date_to):
#             return res
#         
#         employee_id = employee_obj.browse(cr, uid, employee_id, context=context)
#         target_ids = target_obj.get_target(cr, uid, employee_id, date_from, date_to, context=context)
#         if not target_ids:
#             return res
#         
#         target = target_obj.browse(cr, uid, target_ids[0], context=context)
#         res['value']['target_paket'] = target.target_paket
#         res['value']['nilai_target'] = target.nilai_target
#         res['value']['pertambahan_bonus'] = target.pertambahan_bonus
#         res['value']['nilai_bonus'] = target.nilai_bonus
#         res['value']['total_paket'] = delivery_obj.get_delivery(cr, uid, employee_id, date_from, date_to, context=context)
#         return res

    def onchange_employee_id(self, cr, uid, ids, date_from, date_to, employee_id=False, contract_id=False, context=None):
        employee_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        target_obj = self.pool.get('delivery.package.target')
        delivery_obj = self.pool.get('delivery.package.run')
        
        if context is None:
            context = {}
        res = super(HRPayslip, self).onchange_employee_id(cr, uid, ids, date_from, date_to, \
            employee_id=employee_id, contract_id=contract_id, context=context)
#         res['value']['target_paket'] = 0
#         res['value']['nilai_target'] = 0.0
#         res['value']['pertambahan_bonus'] = 0
#         res['value']['nilai_bonus'] = 0.0
        res['value']['total_paket'] = 0

        if (not employee_id) or (not date_from) or (not date_to):
            return res
        
        employee = employee_obj.browse(cr, uid, employee_id, context=context)
        contract = contract_obj.browse(cr, uid, res['value'].get('contract_id', False), context=context)
        target = target_obj.get_target(cr, uid, employee, date_from, date_to, context=context)
        deliveries = delivery_obj.get_deliveries(cr, uid, employee, date_from, date_to, context=context)
        total_consignment = deliveries.get_total_consignment()
        total_courier = deliveries.get_total_courier()
        target_amount = 0.0
        bonus_amount = 0.0
        localdict = dict(result=None, total_consignment=total_consignment, total_courier=total_courier, employee=employee, contract=contract)
        
        if target and target.target_condition(localdict):
            amount, qty = target.compute_target(localdict)
            target_amount = amount * qty
            
        if target and target.bonus_condition(localdict):
            amount, qty = target.compute_bonus(localdict)
            bonus_amount = amount * qty
        
#         target_paket = target and target.target_paket or 0
#         nilai_target = target and target.nilai_target or 0.0
#         pertambahan_bonus = target and target.pertambahan_bonus or 0
#         nilai_bonus = target and target.nilai_bonus or 0.0
#         total_paket = delivery_obj.get_delivery(cr, uid, employee, date_from, date_to, context=context)
#         
#         try:
#             t_bonus = int(((total_paket - target_paket) > 0 and (total_paket - target_paket) or 0) / pertambahan_bonus)
#         except:
#             t_bonus = 0

        input_line_ids = res.get('value', {}) and res.get('value').get('input_line_ids', [])
        for input_line in input_line_ids:
            if input_line.get('code') in ('TARGET', 'TBONUS'):
                if input_line['code'] == 'TARGET':
#                     input_line['amount'] = total_paket and nilai_target or 0.0
                    input_line['amount'] = target_amount
                if input_line['code'] == 'TBONUS':
#                     input_line['amount'] = total_paket and (t_bonus * nilai_bonus) or 0.0
                    input_line['amount'] = bonus_amount
        
#         res['value']['target_paket'] = target_paket
#         res['value']['nilai_target'] = nilai_target
#         res['value']['pertambahan_bonus'] = pertambahan_bonus
#         res['value']['nilai_bonus'] = nilai_bonus
        res['value']['total_paket'] = total_consignment
        return res

# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.exceptions import Warning, ValidationError

import openerp.addons.decimal_precision as dp

class HrBPJSType(models.Model):
    _name = 'hr.bpjs.type'
    _description = "Type of BPJS"
    _order = "name"

    name = fields.Char('BPJS Type', required=True)

class HrBPJSCategory(models.Model):
    _name = 'hr.bpjs.category'
    _description = "Programs of BPJS"
    _order = "type_id, name"

    name = fields.Char('Program of BPJS', required=True)
    code = fields.Char('Code', size=12, required=True)
    type_id = fields.Many2one('hr.bpjs.type', 'BPJS Type', required=True)
    active = fields.Boolean(default=True, help="If the active field is set to False, it will allow you to hide the BPJS program without removing it.")
    amount = fields.Float(required=True, digits=dp.get_precision('Payroll Rate'), help="For BPJS program type percentage, enter % ratio between 0-1.")
    deduction_type = fields.Selection([
            ('percent', 'Percentage'),
            ('fixed', 'Fixed Amount')
        ], required=True, default='percent',
        help="The computation method for the BPJS program amount.\n"
             "* 'Percentage': based on wage for active contract.\n"
             "* 'Fixed Amount': define amount manually.")
    employee_deduction = fields.Boolean()
    
    _sql_constraints = [
            ('code_unique', 'UNIQUE(code)', 'Code must be unique'),
        ]

class HrBPJS(models.Model):
    _name = 'hr.bpjs'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "BPJS Ketenagakerjaan & Kesehatan"

    name = fields.Char('BPJS Number', size=64, required=True, readonly=True, states={'draft': [('readonly', False)]})
    date_registered = fields.Date('Date Registered', default=lambda self: fields.Date.context_today(self), readonly=True, states={'draft': [('readonly', False)]})
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, readonly=True, states={'draft': [('readonly', False)]})
    type_id = fields.Many2one('hr.bpjs.type', 'BPJS Type', required=True, readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
            ('draft', 'Draft'),
            ('registered', 'Registered')
        ], 'State', default='draft', track_visibility='onchange', readonly=True)
    line_ids = fields.One2many('hr.bpjs.line', 'bpjs_id', readonly=True, states={'draft': [('readonly', False)]})
    note = fields.Text('Internal Note')
    
    _sql_constraints = [
            ('name_unique', 'UNIQUE(name)', 'BPJS Number must be unique'),
        ]

    @api.multi
    def action_register(self):
        self.state = 'registered'

    @api.multi
    def action_draft(self):
        self.state = 'draft'


class HrBPJSLine(models.Model):
    _name = 'hr.bpjs.line'
    _description = "Programs of BPJS per type per employee"

    bpjs_id = fields.Many2one('hr.bpjs')
    type_id = fields.Many2one('hr.bpjs.type', related='bpjs_id.type_id')
    category_id = fields.Many2one('hr.bpjs.category', 'BPJS Programs', domain="[('type_id','=',type_id)]", required=True)
    amount = fields.Float(required=True, digits=dp.get_precision('Payroll Rate'), help="For BPJS program type percentage, enter % ratio between 0-1.")
    deduction_type = fields.Selection([
            ('percent', 'Percentage'),
            ('fixed', 'Fixed Amount')
        ], required=True, default='percent',
        help="The computation method for the BPJS program amount.\n"
             "* 'Percentage': based on wage for active contract.\n"
             "* 'Fixed Amount': define amount manually.")
    employee_deduction = fields.Boolean(related='category_id.employee_deduction', readonly=True)

    @api.onchange('category_id')
    def category_change(self):
        if self.category_id:
            self.amount = self.category_id.amount
            self.deduction_type = self.category_id.deduction_type
    
    @api.model
    def get_bpjs_line(self, contract, date_from, date_to, code):
        """
        @param contract: browse record of contract
        @param date_from: date field
        @param date_to: date field
        @param code: char field
        @return: returns the ids of all the bpjs lines for the given contract
        """
        clause_final = [('bpjs_id.employee_id','=',contract.employee_id.id), ('bpjs_id.state','=','registered'), ('category_id.code','=',code)]
        loan_line_ids = self.search(clause_final)
        return loan_line_ids

    @api.multi
    def get_amount(self, contract):
        """
        @return: returns total amount in records
        """
        amount = 0.0
        for l in self:
            if l.deduction_type == 'percent':
                amount += contract.wage * l.amount
            else:
                amount += l.amount
        return amount

    @api.model
    def get_condition(self, code):
        """
        @param code: char field
        @return: returns True or False
        """
        code_from_category = [t.code for t in self.env['hr.bpjs.category'].search([('employee_deduction','=',True)])]
        if code and code in code_from_category:
            return True
        return False

class HRPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    def get_inputs(self, cr, uid, contract_ids, date_from, date_to, context=None):
        result = super(HRPayslip, self).get_inputs(cr, uid, contract_ids, date_from, date_to, context=context)

        contract_obj = self.pool['hr.contract']
        bpjs_line = self.pool['hr.bpjs.line']
        
        for res in result:
            if bpjs_line.get_condition(cr, uid, res.get('code'), context=context):
                contract = contract_obj.browse(cr, uid, [res['contract_id']], context=context)
                bpjs_line_ids = bpjs_line.get_bpjs_line(cr, uid, contract, date_from, date_to, res['code'], context=context)
                if bpjs_line_ids:
                    res['amount'] = bpjs_line_ids.get_amount(contract)
        return result
    
    
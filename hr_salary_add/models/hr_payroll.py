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
import openerp.addons.decimal_precision as dp

class HRPayslipRun(models.Model):
    # Private attributes
    _inherit = 'hr.payslip.run'

    # Default methods
    

    # Fields declaration
    total_amount = fields.Float(digits=dp.get_precision('Payroll'), string='Total Amount', compute='_compute_total_amount', store=True)

    # compute and search fields, in the same order that fields declaration
    @api.one
    @api.depends('slip_ids.net_amount')
    def _compute_total_amount(self):
        total = 0.0
        for slip in self.slip_ids:
            total += slip.net_amount
        self.total_amount = total

    # Constraints and onchanges

    # CRUD methods

    # Action methods

    # Business methods

class HRPayslip(models.Model):
    # Private attributes
    _inherit = 'hr.payslip'

    # Default methods
    

    # Fields declaration
    net_amount = fields.Float(digits=dp.get_precision('Payroll'), string='Net Amount', compute='_compute_net_amount', store=True)

    # compute and search fields, in the same order that fields declaration
    @api.one
    @api.depends('line_ids.code', 'line_ids.total')
    def _compute_net_amount(self):
        amount = 0.0
        for l in self.line_ids:
            if l.code == 'NET':
                amount += l.total
        self.net_amount = amount

    # Constraints and onchanges

    # CRUD methods

    # Action methods

    # Business methods

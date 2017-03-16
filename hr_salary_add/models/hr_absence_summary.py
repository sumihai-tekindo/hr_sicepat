from openerp import models, fields, api, _
from openerp.exceptions import AccessError, Warning

import openerp.addons.decimal_precision as dp


class AbsenceSummary(models.Model):
    _name = "hr.absence.summary"
    
    employee_id = fields.Many2one("hr.employee", string="Nama Karyawan", required=True)
    jumlah_kehadiran = fields.Float(string="Jumlah Hari Kerja", required=True)
    periode = fields.Date(string="Tanggal", required=True, help="Tanggal ini akan diambil ke dalam perhitungan Periode sesuai dengan rules Periode dalam perhitungan Gaji")

    @api.model
    def get_attendances_summary(self, employee, date_from, date_to):
        """
        @param employee: browse record of employee
        @param date_from: date field
        @param date_to: date field
        @return: returns total days of attendance for the given employee that need to be considered for the given dates
        """
        total_attendances = 0.0
        #a contract is valid if it ends between the given dates
        clause_1 = ['&',('periode', '<=', date_to),('periode','>=', date_from)]
        clause_final =  [('employee_id', '=', employee.id)] + clause_1
        attendance_summary_ids = self.search(clause_final)
        if attendance_summary_ids:
            for attendance in attendance_summary_ids:
                total_attendances += attendance.jumlah_kehadiran 
        return total_attendances

class HRPayslip(models.Model):
    _inherit = 'hr.payslip'

    def onchange_employee_id(self, cr, uid, ids, date_from, date_to, employee_id=False, contract_id=False, context=None):
        employee_obj = self.pool.get('hr.employee')
        attendance_summary_obj = self.pool.get('hr.absence.summary')
        
        if context is None:
            context = {}
        res = super(HRPayslip, self).onchange_employee_id(cr, uid, ids, date_from, date_to, \
            employee_id=employee_id, contract_id=contract_id, context=context)

        if (not employee_id) or (not date_from) or (not date_to):
            return res
        
        employee_id = employee_obj.browse(cr, uid, employee_id, context=context)
        if employee_id.summarized_attendances:
            attendances_summary = attendance_summary_obj.get_attendances_summary(cr, uid, employee_id, date_from, date_to, context=context)
            worked_days_line_ids = res.get('value', {}) and res.get('value').get('worked_days_line_ids', [])
            for worked_days_line in worked_days_line_ids:
                if worked_days_line.get('code') == ('SISO'):
                    worked_days_line['number_of_days'] = attendances_summary or 0.0
                    worked_days_line['number_of_hours'] = 0.0

        return res

class res_company(models.Model):
    _inherit = "res.company"

    summarized_attendances = fields.Boolean(string='Summarized Attendances', default=True)
    
class HumanResourcesConfiguration(models.TransientModel):
    _inherit = 'hr.config.settings'

    summarized_attendances = fields.Boolean(string='Summarized Attendances')

    @api.model
    def get_default_summarized_attendances_values(self, fields):
        company = self.env.user.company_id
        return {
            'summarized_attendances': company.summarized_attendances,
        }

    @api.one
    def set_summarized_attendances_values(self):
        company = self.env.user.company_id
        company.summarized_attendances = self.summarized_attendances


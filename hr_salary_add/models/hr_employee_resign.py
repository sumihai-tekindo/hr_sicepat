from openerp import api, fields, models
from openerp.exceptions import Warning
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class HREmployeeResign(models.Model):
    _name = 'hr.employee.resign'
    
    name = fields.Char(string='Number', readonly=True)
    request_id = fields.Many2one('res.users', string='Requestor', readonly=True,
        default=lambda self: self.env.user)
    tanggal = fields.Date(default=lambda self: fields.Date.context_today(self), readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    employee_id = fields.Many2one('hr.employee', string='Nama Karyawan', required=True, readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    job_id = fields.Many2one('hr.job', string='Jabatan', related='employee_id.job_id', readonly=True)
    department_id = fields.Many2one('hr.department', string='Cabang', related='employee_id.department_id', 
        readonly=True)
    alasan = fields.Text(readonly=True,
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    state = fields.Selection([
        ('draft','Open'),
        ('submit','Submit'),
        ('reject','Reject'),
        ('approved','Approved'),
        ('terminate','Terminate'),
        ], string='Status', default='draft')
    
    @api.multi
    def action_submit(self):
        employee = self.env['hr.employee'].search([('id','=',self.employee_id.id)])
        if(employee.sisa_pinjaman==0):
            self.state = 'submit'
        else:
            raise Warning(_("Masih ada outstanding piutang karyawan. Silahkan di selesaikan terlebih dahulu, baru Submit pengajuan Karyawan Resign ini."))

    @api.multi
    def action_approve(self):
        self.state = 'approved'
#         employee = self.env['hr.employee'].search([('id','=',self.employee_id.id)])
#         employee.write({'active':False})
        contract = self.env['hr.contract'].search([('employee_id','=',self.employee_id.id)])
        contract.write({'date_end':self.tanggal})
        
    @api.multi
    def action_reject(self):
        self.state = 'reject'
        
    @api.multi
    def action_terminate(self):
        self.state = 'terminate'
        employee = self.env['hr.employee'].search([('id','=',self.employee_id.id)])
        employee.write({'active':False})


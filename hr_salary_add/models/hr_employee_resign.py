from openerp import api, fields, models
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
        ], string='Status', default='draft')
    
    @api.multi
    def action_submit(self):
        self.state = 'submit'

    @api.multi
    def action_approve(self):
        self.state = 'approved'
        employee = self.env['hr.employee'].search([('id','=',self.employee_id.id)])
        employee.write({'active':False})
        contract = self.env['hr.contract'].search([('employee_id','=',self.employee_id.id)])
        contract.write({'date_end':self.tanggal})
        
    @api.multi
    def action_reject(self):
        self.state = 'reject'


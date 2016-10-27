from openerp import models, fields, api
import openerp.addons.decimal_precision as dp

class hr_salary_proposal(models.Model):
    _name = "hr_salary_proposal"
    
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
    
    @api.multi
    def action_submit(self):
        self.state = 'submit'

    @api.multi
    def action_approve(self):
        self.state = 'approved'
        
    @api.multi
    def action_reject(self):
        self.state = 'reject'
        
    @api.one
    @api.depends('wage','kenaikan_gaji')
    def compute_gaji(self):
#         if((self.gaji_semula!=0) and (self.kenaikan_gaji!=0)):
#             self.gaji_usulan = self.gaji_semula+self.kenaikan_gaji
        self.gaji_semula = self.wage
        self.gaji_usulan = self.gaji_semula + self.kenaikan_gaji
            
    @api.onchange('nama_karyawan','tanggal')
    def onchange_karyawan(self):
        self.nama_cabang = False
        self.jabatan = False
        self.contract_id = False
        self.wage = 0.0
        
        if self.nama_karyawan:
            self.nama_cabang = self.nama_karyawan.department_id and self.nama_karyawan.department_id.id or False
            self.jabatan = self.nama_karyawan.job_id and self.nama_karyawan.job_id.id or False
            contract_ids = self.env['hr.payslip'].get_contract(self.nama_karyawan, self.tanggal, self.tanggal)
            if contract_ids:
                contract = self.env['hr.contract'].browse(contract_ids[0])
                print('contract_id: %s' % contract.id)
                self.contract_id = contract and contract.id or False
                self.wage = contract and contract.wage or False
            
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get("salary.proposal")
        employee = self.env['hr.employee'].search([('id','=',vals['nama_karyawan'])])
        vals['nama_cabang'] = employee.department_id and employee.department_id.id or False
        vals['jabatan'] = employee.job_id and employee.job_id.id or False
        return super(hr_salary_proposal, self).create(vals)
    
    @api.multi
    def write(self, vals):
        if vals.get('nama_karyawan'):
            employee = self.env['hr.employee'].search([('id','=',vals.get('nama_karyawan'))])
            vals['nama_cabang'] = employee.department_id and employee.department_id.id or False
            vals['jabatan'] = employee.job_id and employee.job_id.id or False
        return super(hr_salary_proposal, self).write(vals)
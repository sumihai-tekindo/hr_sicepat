from openerp import models, fields, api
import openerp.addons.decimal_precision as dp

class hr_salary_proposal(models.Model):
    _name = "hr_salary_proposal"
    
    name = fields.Char(string="code", default=lambda self: self.env['ir.sequence'].get("salary.proposal"))
    
    tanggal = fields.Date(default=lambda self: fields.Date.context_today(self))
    requestor = fields.Many2one('res.users', string="Requestor", default=lambda self: self.env.user)
    nama_cabang = fields.Many2one('account.analytic.account', string="Nama Cabang", required=True)
    nama_karyawan = fields.Many2one("hr.employee", string="Nama Karyawan", required=True)
    jabatan = fields.Many2one('hr.job', string="Jabatan", required=True)
    gaji_semula = fields.Float(digits=dp.get_precision('Payroll'), string="Gaji Awal", required=True)
    kenaikan_gaji = fields.Float(digits=dp.get_precision('Payroll'), string="Kenaikan Gaji", required=True)
    gaji_usulan = fields.Float(digits=dp.get_precision('Payroll'), string="Gaji Usulan", compute="compute_gaji_usulan", required=True)
    alasan = fields.Text()
    
    state = fields.Selection([
            ('open','Open'),
            ('submit','Submit'),
            ('reject','Reject'),
            ('approved','Approved'),
        ], string='Status', default='open')
    
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
    @api.depends('gaji_semula','kenaikan_gaji')
    def compute_gaji_usulan(self):
        if((self.gaji_semula!=0) and (self.kenaikan_gaji!=0)):
            self.gaji_usulan = self.gaji_semula+self.kenaikan_gaji
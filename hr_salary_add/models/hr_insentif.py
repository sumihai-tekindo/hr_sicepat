from openerp import models, fields,api
import openerp.addons.decimal_precision as dp

class hr_insentif(models.Model):
    _name = "hr_insentif"
    
    name = fields.Char(string="code")
    
    tanggal = fields.Date(default=lambda self: fields.Date.context_today(self))
    requestor = fields.Many2one('res.users', string="Requestor", default=lambda self: self.env.user)
    nama_koordinator = fields.Many2one('hr.employee', string="Nama Koordinator Wilayah")
    nama_karyawan = fields.Many2one("hr.employee", string="Nama Karyawan", required=True)
    jabatan = fields.Many2one("hr.job", string="Jabatan", required=True)
    nama_cabang = fields.Many2one("account.analytic.account", string="Nama Cabang", required=True)
    nilai_insentif = fields.Float(digits=dp.get_precision('Payroll'), string="Nilai Insentif", required=True)
    alasan = fields.Char()
    state = fields.Selection([
            ('open','Open'),
            ('submit','Submit'),
            ('reject','Reject'),
            ('approved','Approved'),
        ], string='Status Page', default='open')
    
    @api.multi
    def action_submit(self):
        self.state = 'submit'

    @api.multi
    def action_approve(self):
        self.state = 'approved'
        
    @api.multi
    def action_reject(self):
        self.state = 'reject'
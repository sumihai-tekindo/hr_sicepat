from openerp import models, fields,api
import openerp.addons.decimal_precision as dp

class hr_insentif(models.Model):
    _name = "hr_insentif"
    
    name = fields.Char(string="code")
    
    tanggal = fields.Date()
    requestor = fields.Many2one('res.users', string="Requestor")
    nama_koordinator = fields.Many2one('res.users', string="Nama Koordinator Wilayah")
    nama_karyawan = fields.Many2one("hr.employee", string="Nama Karyawan")
    jabatan = fields.Many2one("hr.job", string="Jabatan")
    nama_cabang = fields.Many2one("account.analytic.account", string="Nama Cabang")
    nilai_insentif = fields.Float(digits=dp.get_precision('Payroll'), string="Nilai Tunjangan Lain-lain")
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
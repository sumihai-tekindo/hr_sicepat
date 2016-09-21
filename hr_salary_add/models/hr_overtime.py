from openerp import models, fields, api
import openerp.addons.decimal_precision as dp

class hr_overtime(models.Model):
    _name = "hr_overtime"
    
    name = fields.Char(string="code")
    tanggal = fields.Date()
    requestor = fields.Many2one('res.users', string="Requestor")
    nama_cabang = fields.Many2one('account.analytic.account', string="Nama Cabang")
    nik = fields.Many2one("hr.employee", string="NIK")
    nama_karyawan = fields.Many2one("hr.employee", string="Nama Karyawan")
    nilai = fields.Float(digits=dp.get_precision('Payroll'), string="Nilai")
    alasan = fields.Text()
    status = fields.Selection([
            ('draft','Draft'),
            ('approve','Approve'),
            ('reject','Reject'),
        ], string='Status', default='draft')
    state = fields.Selection([
            ('open','Open'),
            ('submit','Submit'),
            ('approved','Approved'),
            ('proses','Proses Di Gaji'),
            ('reject','Reject'),
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
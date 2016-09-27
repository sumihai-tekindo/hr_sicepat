from openerp import models, fields, api
import openerp.addons.decimal_precision as dp

class hr_overtime(models.Model):
    _name = "hr_overtime"
    
    name = fields.Char(string="code")
    tanggal = fields.Date()
    requestor = fields.Many2one('res.users', string="Requestor")
    nama_cabang = fields.Many2one('account.analytic.account', string="Nama Cabang")
    overtime_ids = fields.One2many('hr_overtime_line','overtime_id')
    
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

class hr_overtime_line(models.Model):
    _name = "hr_overtime_line"
    
    name = fields.Char(string="code")
    overtime_id = fields.Many2one('hr_overtime')
    nik = fields.Many2one("hr.employee", string="NIK")
    nama_karyawan = fields.Many2one("hr.employee", string="Nama Karyawan")
    nilai = fields.Float(digits=dp.get_precision('Payroll'), string="Nilai")
    alasan = fields.Text()
    state = fields.Selection([
            ('draft','Draft'),
            ('confirmed','Confirmed'),
            ('cancel','Cancel'),
        ], string='Status', default='draft')
    
    @api.multi
    def action_confirm(self):
        self.state = 'confirmed'
        
    @api.multi
    def action_cancel(self):
        self.state = 'cancel'
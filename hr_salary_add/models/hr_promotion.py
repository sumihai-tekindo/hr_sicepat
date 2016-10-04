from openerp import models, fields, api

class hr_promotion(models.Model):
    _name = "hr_promotion"
    
    name = fields.Char(string="code")
    
    tanggal = fields.Date()
    requestor = fields.Many2one('res.users', string="Requestor")
    
    nama_karyawan = fields.Many2one("hr.employee", string="Nama Karyawan")
    jabatan_awal = fields.Many2one('hr.job', string="Jabatan")
    cabang_awal = fields.Many2one('account.analytic.account', string="Cabang Asal")
    usulan_jabatan_baru = fields.Many2one('hr.job', string="Usulan Jabatan")
    cabang_baru = fields.Many2one('account.analytic.account', string="Cabang Baru")
    
    state = fields.Selection([
            ('open','Open'),
            ('submit','Submit'),
            ('reject','Reject'),
            ('approved','Approved'),
        ], string='State', default='open')
    
    @api.multi
    def action_submit(self):
        self.state = 'submit'

    @api.multi
    def action_approve(self):
        self.state = 'approved'
        
    @api.multi
    def action_reject(self):
        self.state = 'reject'
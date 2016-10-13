from openerp import models, fields, api

class hr_memorandum(models.Model):
    _name = "hr_memorandum"
    
    name = fields.Char(string="code")
    
    tanggal = fields.Date(default=lambda self: fields.Date.context_today(self))
    nama_karyawan = fields.Many2one("hr.employee", string="Nama Karyawan", required=True)
    nama_atasan = fields.Many2one("hr.employee", string="Nama Atasan", required=True)
    jabatan = fields.Many2one('hr.job', string="Jabatan", required=True)
    nama_cabang = fields.Many2one('account.analytic.account', string="Nama Cabang", required=True)
    alasan = fields.Text()
    flag = fields.Boolean()
    
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
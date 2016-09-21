from openerp import models, fields, api

class hr_salary_particular(models.Model):
    _name = "hr_salary_proposal"
    
    name = fields.Char(string="code")
    
    tanggal = fields.Date()
    requestor = fields.Many2one('res.users', string="Requestor")
    nama_cabang = fields.Many2one('account.analytic.account', string="Nama Cabang")
    nama_karyawan = fields.Many2one("hr.employee", string="Nama Karyawan")
    jabatan = fields.Many2one('hr.job', string="Jabatan")
    gaji_semula = fields.Integer()
    kenaikan_gaji = fields.Integer()
    gaji_usulan = fields.Integer()
    alasan = fields.Text()
    
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
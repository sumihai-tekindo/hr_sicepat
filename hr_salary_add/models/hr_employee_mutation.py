from openerp import models, fields, api

class hr_employee_mutation(models.Model):
    _name = "hr_employee_mutation"
    
    name = fields.Char(string="code")
    
    tanggal = fields.Date()
    requestor = fields.Many2one('res.users', string="Requestor")
    
    nama_karyawan = fields.Many2one("hr.employee", string="Nama Karyawan")
    cabang_awal = fields.Many2one('account.analytic.account', string="Cabang Asal")
    cabang_baru = fields.Many2one('account.analytic.account', string="Cabang Baru")
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
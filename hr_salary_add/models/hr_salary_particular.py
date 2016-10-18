from openerp import models, fields, api
import openerp.addons.decimal_precision as dp

class hr_salary_particular(models.Model):
    _name = "hr_salary_particular"
    
    name = fields.Char(string="code", default=lambda self: self.env['ir.sequence'].get("salary.particular"))
    
    tanggal = fields.Date(default=lambda self: fields.Date.context_today(self))
    requestor = fields.Many2one('res.users', string="Requestor", default=lambda self: self.env.user)
    nama_cabang = fields.Many2one('account.analytic.account', string="Nama Cabang", required=True)
    jabatan = fields.Many2one('hr.job', string="Jabatan", required=True)
#     nilai_insentif = fields.Float(digits=dp.get_precision('Payroll'), string="Nilai Insentif")
    uang_makan = fields.Float(digits=dp.get_precision('Payroll'), string="Uang Makan")
    transport = fields.Float(digits=dp.get_precision('Payroll'), string="Transport")
    uang_kerajinan = fields.Float(digits=dp.get_precision('Payroll'), string="Uang Kerajinan")
    tunj_operasional = fields.Float(digits=dp.get_precision('Payroll'), string="Tunjangan Operasional")
    tunj_jabatan = fields.Float(digits=dp.get_precision('Payroll'), string="Tunjangan Jabatan")
    service_motor = fields.Float(digits=dp.get_precision('Payroll'), string="Service Motor")
    
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
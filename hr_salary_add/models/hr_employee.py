from openerp import models, fields, api
import openerp.addons.decimal_precision as dp

class hr_employee(models.Model):
    _inherit = 'hr.employee'
    
    sisa_pinjaman = fields.Float(digits=dp.get_precision('Payroll'), string="Sisa Pinjaman", compute="compute_sisa_pinjaman")
    flag = fields.Boolean(compute="compute_flag", string="Status SP")
    loan_ids = fields.One2many("hr_loan","nama_karyawan")
    memorandum_ids = fields.One2many("hr_memorandum","nama_karyawan")
    referensi = fields.Selection([
            ('jobdb','jobsDB'),
            ('koran','Koran'),
            ('karyawan','karyawan'),
        ], string='Referensi')
    
    @api.one
    @api.depends('loan_ids.sisa_pinjaman')
    def compute_sisa_pinjaman(self):
        loans = self.env['hr_loan'].search([('nama_karyawan','=',self.id)]) or False
        sisa_pinjaman_temp = 0
        if(loans):
            for loan in loans:
                sisa_pinjaman_temp += loan.sisa_pinjaman
        self.sisa_pinjaman = sisa_pinjaman_temp
        
    @api.one
    @api.depends('memorandum_ids.flag')
    def compute_flag(self):
        sp = self.env['hr_memorandum'].search([('nama_karyawan','=',self.id)]) or False
        if(sp):
            self.flag = sp.flag
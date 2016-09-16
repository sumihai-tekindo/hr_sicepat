from openerp import models, fields
import openerp.addons.decimal_precision as dp

class hr_salary_particular(models.Model):
    _name = "hr_salary_particular"
    
    name = fields.Char(string="code")
    tanggal = fields.Date()
    requestor = fields.Many2one('res.users', string="Requestor")
    nama_cabang = fields.Many2one('account.analytics.account', string="Nama Cabang")
    jabatan = fields.Many2one('hr.job', string="Jabatan")
    nilai_insentif = fields.Float(digits=dp.get_precision('Payroll'), string="Nilai Insentif")
    uang_makan = fields.Float(digits=dp.get_precision('Payroll'), string="Uang Makan")
    service_motor = fields.Float(digits=dp.get_precision('Payroll'), string="Service Motor")
    uang_kerajinan = fields.Float(digits=dp.get_precision('Payroll'), string="Uang Kerajinan")
    tunj_kerja_malam = fields.Float(digits=dp.get_precision('Payroll'), string="Tunjangan Kerja Malam")
    tunj_jabatan = fields.Float(digits=dp.get_precision('Payroll'), string="Tunjangan Jabatan")
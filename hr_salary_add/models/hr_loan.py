from openerp import models, fields
import openerp.addons.decimal_precision as dp

class hr_loan(models.Model):
    _name = "hr_loan"
    
    name = fields.Char()
    tanggal = fields.Date()
    nama_karyawan = fields.Many2one("hr.employee", string="Nama Karyawan")
    jabatan = fields.Many2one('hr.job', string="Jabatan")
    nama_cabang = fields.Many2one('account.analytic.account', string="Nama Cabang")
    nilai_pinjaman = fields.Float(digits=dp.get_precision('Payroll'), string="Nilai")
    nilai_potongan_gaji = fields.Float(digits=dp.get_precision('Payroll'), string="Nilai")
    bulan_awal_pemotongan = fields.Char()
    
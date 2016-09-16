from openerp import models, fields
import openerp.addons.decimal_precision as dp

class hr_other_allowence(models.Model):
    _name = "hr_other_allowence"
    
    name = fields.Char(string="code")
    tanggal = fields.Date()
    requestor = fields.Many2one('res.users', string="Requestor")
    nama_koordinator = fields.Many2one('res.users', string="Nama Koordinator Wilayah")
    nama_karyawan = fields.Many2one("hr.employee", string="Nama Karyawan")
    jabatan = fields.Many2one("hr.job", string="Jabatan")
    nama_cabang = fields.Many2one("account.analytic.account", string="Nama Cabang")
    nilai_tunj_lain = fields.Float(digits=dp.get_precision('Payroll'), string="Nilai Tunjangan Lain-lain")
    alasan = fields.Char()
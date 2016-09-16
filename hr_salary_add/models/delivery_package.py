from openerp import models, fields
import openerp.addons.decimal_precision as dp

class delivery_package(models.Model):
    _name = "delivery_package"
    
    name = fields.Char()
    periode = fields.Many2one('account.period', string = "Periode")
    nama_cabang = fields.Many2one('account.analytics.account', string="Nama Cabang")
    target_paket = fields.Integer()
    target_paket_bulan_lalu = fields.Integer()
    pertambahan_bonus = fields.Float(digits=dp.get_precision('Payroll'), string="Pertambahan Bonus")
    pertambahan_bonus_bulan_lalu = fields.Float(digits=dp.get_precision('Payroll'), string="Pertambahan Bonus Bulan Lalu")
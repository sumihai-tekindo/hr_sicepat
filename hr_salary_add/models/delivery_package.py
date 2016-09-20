from openerp import models, fields, api
import openerp.addons.decimal_precision as dp

class delivery_package(models.Model):
    _name = "delivery_package"
    
    name = fields.Char()
    periode = fields.Many2one('account.period', string = "Periode")
    nama_cabang = fields.Many2one('account.analytic.account', string="Nama Cabang")
    target_paket = fields.Integer()
    target_paket_bulan_lalu = fields.Integer()
    pertambahan_bonus = fields.Float(digits=dp.get_precision('Payroll'), string="Pertambahan Bonus")
    pertambahan_bonus_bulan_lalu = fields.Float(digits=dp.get_precision('Payroll'), string="Pertambahan Bonus Bulan Lalu")
    state = fields.Selection([
            ('open','Open'),
            ('submit','Submit'),
            ('reject','Reject'),
            ('approved','Approved'),
        ], string='Status Page', default='open')
    
    @api.multi
    def action_submit(self):
        self.state = 'submit'

    @api.multi
    def action_approve(self):
        self.state = 'approved'
        
    @api.multi
    def action_reject(self):
        self.state = 'reject'
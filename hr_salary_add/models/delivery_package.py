from openerp import models, fields, api
import openerp.addons.decimal_precision as dp
from reportlab.lib.pdfencrypt import computeO

class delivery_package(models.Model):
    _name = "delivery_package"
    
    name = fields.Char(string="code", default=lambda self: self.env['ir.sequence'].get("delivery.package"))
    periode = fields.Many2one('account.period', string = "Periode", required=True)
    nama_cabang = fields.Many2one('account.analytic.account', string="Nama Cabang", required=True)
    target_paket = fields.Integer(required=True)
    target_paket_bulan_lalu = fields.Integer(compute="compute_target_bulan_lalu", store=1)
    pertambahan_bonus = fields.Integer(string="Pertambahan Bonus", required=True)
    pertambahan_bonus_bulan_lalu = fields.Integer(string="Pertambahan Bonus Bulan Lalu", compute="compute_target_bulan_lalu", store=1)
    state = fields.Selection([
            ('open','Open'),
            ('submit','Submit'),
            ('reject','Reject'),
            ('approved','Approved'),
        ], string='Status', default='open')
    
    @api.multi
    def action_submit(self):
        self.state = 'submit'

    @api.multi
    def action_approve(self):
        self.state = 'approved'
        
    @api.multi
    def action_reject(self):
        self.state = 'reject'
        
    @api.one
    @api.depends('nama_cabang','periode','target_paket','pertambahan_bonus')
    def compute_target_bulan_lalu(self):
        print('panggil compute')
        dp = self.search([('nama_cabang','=',self.nama_cabang.id)], order='periode desc') or False
        if(dp):
            self.target_paket_bulan_lalu = dp[0].target_paket
            self.pertambahan_bonus_bulan_lalu = dp[0].pertambahan_bonus
            
    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        print('ini create', vals)
        return super(delivery_package,self).create(vals)
    
    @api.multi
    def write(self, vals):
        print('ini write', vals)
        return super(delivery_package,self).write(vals)
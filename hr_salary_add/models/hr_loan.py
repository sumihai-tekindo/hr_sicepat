from openerp import models, fields, api
from openerp.osv import osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class hr_loan(models.Model):
    _name = "hr_loan"
    
    name = fields.Char(string="code")
    tanggal = fields.Date(default=lambda self: fields.Date.context_today(self))
    nama_karyawan = fields.Many2one("hr.employee", string="Nama Karyawan")
    jabatan = fields.Many2one('hr.job', string="Jabatan")
    nama_cabang = fields.Many2one('account.analytic.account', string="Nama Cabang")
    nilai_pinjaman = fields.Float(digits=dp.get_precision('Payroll'), string="Nilai Pinjaman")
    jumlah_cicilan = fields.Integer()
    cicilan_per_bulan = fields.Float(digits=dp.get_precision('Payroll'), string="Cicilan Per Bulan")
    bulan_awal_pemotongan = fields.Date()
    keperluan = fields.Char()
    nama_bank = fields.Char()
    no_rekening = fields.Char()
    alasan_reject = fields.Char()
    loan_ids = fields.One2many("hr_loan_line","loan_id")
    
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
        
    @api.multi
    def compute_cicilan_per_bulan(self, nilai_pinjaman, jumlah_cicilan):
#         print('test tes tes')
        print('nilai pinjaman : %s dan jumlah cicilan : %s' % (nilai_pinjaman,jumlah_cicilan))
        if((nilai_pinjaman!=0) and (jumlah_cicilan!=0)):
            return {'value': {'cicilan_per_bulan':(nilai_pinjaman/jumlah_cicilan)}}
#             raise osv.except_osv(_('Jumlah cicilan anda kurang dari minimum!'), _('atau melebihi Sisa Pinjaman Anda.'))

class hr_loan_line(models.Model):
    _name = "hr_loan_line"
    
    name = fields.Char(string="code")
    loan_id = fields.Many2one("hr_loan")
    tanggal_cicil = fields.Date()
    nilai_cicilan = fields.Float(digits=dp.get_precision('Payroll'), string="Nilai Cicilan")
    total_nilai_cicilan = fields.Float(digits=dp.get_precision('Payroll'), string="Total Nilai Cicilan")
    sisa_pinjaman = fields.Float(digits=dp.get_precision('Payroll'), string="Sisa Pinjaman")
    keterangan = fields.Char()
    posted = fields.Boolean()
    
    @api.multi
    def compute_nilai_cicilan(self, nilai_cicilan, cicilan_per_bulan, nilai_pinjaman):
        ctx = self._context
        loan_id = ctx.get('loan_id',False)
        loan_line = self.search([('loan_id','=',loan_id)], order='sisa_pinjaman desc')
        if loan_line:
            loan_line = self.search([('loan_id','=',loan_id)], order='sisa_pinjaman desc')[0]
            if (((nilai_cicilan < cicilan_per_bulan) or (nilai_cicilan > loan_line.sisa_pinjaman)) and (nilai_cicilan != 0)):
                raise osv.except_osv(_('Jumlah cicilan anda kurang dari minimum!'), _('atau melebihi Sisa Pinjaman Anda.'))
            else:
                return {
                    'value': {'total_nilai_cicilan':loan_line.total_nilai_cicilan+nilai_cicilan,
                              'sisa_pinjaman':loan_line.sisa_pinjaman-nilai_cicilan}
                    }
        else:
            if(((nilai_cicilan < cicilan_per_bulan) or (nilai_cicilan>nilai_pinjaman))and (nilai_cicilan != 0)):
                raise osv.except_osv(_('Jumlah cicilan anda kurang dari minimum!'), _('atau melebihi Sisa Pinjaman Anda.'))
            else:
                return {
                    'value': {'total_nilai_cicilan':nilai_cicilan,
                              'sisa_pinjaman':nilai_pinjaman-nilai_cicilan}
                    }

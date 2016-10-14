from openerp import models, fields, api
from openerp.osv import osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class hr_loan(models.Model):
    _name = "hr_loan"
    
    name = fields.Char(string="code")
    tanggal = fields.Date(default=lambda self: fields.Date.context_today(self))
    nama_karyawan = fields.Many2one("hr.employee", string="Nama Karyawan", required=True)
    jabatan = fields.Many2one('hr.job', string="Jabatan", required=True)
    nama_cabang = fields.Many2one('account.analytic.account', string="Nama Cabang", required=True)
    nilai_pinjaman = fields.Float(digits=dp.get_precision('Payroll'), string="Nilai Pinjaman", required=True)
    jumlah_cicilan = fields.Integer(required=True)
    cicilan_per_bulan = fields.Float(digits=dp.get_precision('Payroll'), string="Cicilan Per Bulan", compute="compute_cicilan_per_bulan")
    bulan_awal_pemotongan = fields.Date(required=True)
    keperluan = fields.Char()
    nama_bank = fields.Char()
    no_rekening = fields.Char(required=True)
    alasan_reject = fields.Char()
    loan_ids = fields.One2many("hr_loan_line","loan_id")
    sisa_pinjaman = fields.Float(digits=dp.get_precision('Payroll'), string="Sisa Pinjaman", compute="compute_sisa_pinjaman", store=1)
    
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
        
    @api.one
    @api.depends('nilai_pinjaman','jumlah_cicilan')
    def compute_cicilan_per_bulan(self):
        if((self.nilai_pinjaman!=0) and (self.jumlah_cicilan!=0)):
            self.cicilan_per_bulan = self.nilai_pinjaman/self.jumlah_cicilan
    
    @api.one
    @api.depends('loan_ids.sisa_pinjaman')
    def compute_sisa_pinjaman(self):
        loan_lines = self.env['hr_loan_line'].search([('loan_id','=',self.id)], order='sisa_pinjaman asc') or False
        if(loan_lines):
            self.sisa_pinjaman = loan_lines[0].sisa_pinjaman
        
#     @api.multi
#     def compute_pinjaman(self,loan_id):
#         loans = self.browse([loan_id])
#         total_nilai_cicilan = 0.0
#         sisa_pinjaman = 0.0
#         print(loans)
#         for line in loans.loan_ids:
#             print('total nilai cicilan %s dan sisa pinjaman %s' % (line.total_nilai_cicilan,line.sisa_pinjaman), line.id)
#             if(line.total_nilai_cicilan > total_nilai_cicilan):
#                 total_nilai_cicilan = line.total_nilai_cicilan
#                 sisa_pinjaman = line.sisa_pinjaman
#                 
#         return total_nilai_cicilan,sisa_pinjaman
    
#     @api.multi
#     def compute_cicilan_per_bulan(self, nilai_pinjaman, jumlah_cicilan):
# #         print('test tes tes')
#         print('nilai pinjaman : %s dan jumlah cicilan : %s' % (nilai_pinjaman,jumlah_cicilan))
#         if((nilai_pinjaman!=0) and (jumlah_cicilan!=0)):
#             return {'value': {'cicilan_per_bulan':(nilai_pinjaman/jumlah_cicilan)}}
# #             raise osv.except_osv(_('Jumlah cicilan anda kurang dari minimum!'), _('atau melebihi Sisa Pinjaman Anda.'))

class hr_loan_line(models.Model):
    _name = "hr_loan_line"
    
    name = fields.Char(string="code")
    loan_id = fields.Many2one("hr_loan")
    tanggal_cicil = fields.Date(default=lambda self: fields.Date.context_today(self))
    nilai_cicilan = fields.Float(digits=dp.get_precision('Payroll'), string="Nilai Cicilan")
    total_nilai_cicilan = fields.Float(digits=dp.get_precision('Payroll'), string="Total Nilai Cicilan")
    sisa_pinjaman = fields.Float(digits=dp.get_precision('Payroll'), string="Sisa Pinjaman")
    keterangan = fields.Char()
    posted = fields.Boolean()
    
    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        loan_id = vals.get('loan_id')
        loan = self.env['hr_loan'].browse([loan_id])
        self.env['hr_loan'].compute_sisa_pinjaman()
        if((vals.get('nilai_cicilan') < loan.cicilan_per_bulan) or (vals.get('total_nilai_cicilan') > loan.nilai_pinjaman) or (vals.get('sisa_pinjaman') < 0)):
            raise osv.except_osv(_('Gagal Menyimpan!'), _('Jumlah cicilan anda kurang dari minimum atau melebihi Sisa Pinjaman Anda.'))
        else:
            result = super(hr_loan_line,self).create(vals)
#             loan.compute_sisa_pinjaman()
        return result
    
    @api.multi
    def compute_nilai_cicilan(self, nilai_cicilan, cicilan_per_bulan, nilai_pinjaman):
        ctx = self._context
        loan_id = ctx.get('loan_id',False)
        loan_lines = self.search([('loan_id','=',loan_id)], order='sisa_pinjaman asc') or False
        if loan_lines:
            if (((nilai_cicilan < cicilan_per_bulan) or (nilai_cicilan > loan_lines[0].sisa_pinjaman)) and (nilai_cicilan != 0)):
#                 raise osv.except_osv(_('Jumlah cicilan anda kurang dari minimum!'), _('atau melebihi Sisa Pinjaman Anda.'))
                return {
                    'value': {'total_nilai_cicilan':loan_lines[0].total_nilai_cicilan+nilai_cicilan,
                              'sisa_pinjaman':loan_lines[0].sisa_pinjaman-nilai_cicilan}
                    }
            else:
                return {
                    'value': {'total_nilai_cicilan':loan_lines[0].total_nilai_cicilan+nilai_cicilan,
                              'sisa_pinjaman':loan_lines[0].sisa_pinjaman-nilai_cicilan}
                    }
        else:
            if(((nilai_cicilan < cicilan_per_bulan) or (nilai_cicilan>nilai_pinjaman))and (nilai_cicilan != 0)):
                return {
                        'value': {'total_nilai_cicilan':nilai_cicilan,
                                  'sisa_pinjaman':nilai_pinjaman-nilai_cicilan}
                        }
#                 raise osv.except_osv(_('Jumlah cicilan anda kurang dari minimum!'), _('atau melebihi Sisa Pinjaman Anda.'))
            else:
                return {
                    'value': {'total_nilai_cicilan':nilai_cicilan,
                              'sisa_pinjaman':nilai_pinjaman-nilai_cicilan}
                    }

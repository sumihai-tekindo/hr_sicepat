from openerp import models, fields, api
import openerp.addons.decimal_precision as dp

class hr_employee_agama(models.Model):
    _name = 'hr.employee.agama'

    name = fields.Char(string="Nama")

class hr_employee_pendidikan(models.Model):
    _name = 'hr.employee.pendidikan'

    name = fields.Char(string="Nama")
    
class hr_employee(models.Model):
    _inherit = 'hr.employee'
    
    flag = fields.Boolean(readonly=True, string="Status SP")
#     memorandum_ids = fields.One2many("hr_memorandum","nama_karyawan")
    referensi = fields.Selection([
            ('jobdb','jobsDB'),
            ('koran','Koran'),
            ('karyawan','karyawan'),
        ], string='Referensi')
    sts_karyawan = fields.Selection([
            ('ojt','On The Job Training'),
            ('pjs','Promosi Jabatan Sementara'),
            ('kontrak','Kontrak'),
            ('kartap','Karyawan Tetap'),
        ], string='Status Karyawan')
    no_npwp = fields.Char(string="Nomor NPWP")
    active = fields.Boolean(related="resource_id.active", store=True, track_visibility="onchange")
    agama_id = fields.Many2one("hr.employee.agama", string = "Religion")
    pendidikan_id = fields.Many2one("hr.employee.pendidikan", string = "Qualification")
    bank_account_id = fields.Many2one("res.partner.bank", track_visibility="onchange")
    bank_account_number = fields.Char(string="Account Number", track_visibility='always')


    @api.onchange('bank_account_id')
    def onchange_bank_account(self):
        if self.bank_account_id:
            self.bank_account_number = self.bank_account_id.acc_number


from openerp import models, fields, api
import openerp.addons.decimal_precision as dp

class hr_employee(models.Model):
    _inherit = 'hr.employee'
    
    flag = fields.Boolean(readonly=True, string="Status SP")
#     memorandum_ids = fields.One2many("hr_memorandum","nama_karyawan")
    referensi = fields.Selection([
            ('jobdb','jobsDB'),
            ('koran','Koran'),
            ('karyawan','karyawan'),
        ], string='Referensi')
    no_npwp = fields.Char(string="Nomor NPWP")
    active = fields.Boolean(track_visibility="onchange")
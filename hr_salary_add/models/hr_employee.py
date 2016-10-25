from openerp import models, fields, api
import openerp.addons.decimal_precision as dp

class hr_employee(models.Model):
    _inherit = 'hr.employee'
    
    flag = fields.Boolean(compute="compute_flag", string="Status SP")
    memorandum_ids = fields.One2many("hr_memorandum","nama_karyawan")
    referensi = fields.Selection([
            ('jobdb','jobsDB'),
            ('koran','Koran'),
            ('karyawan','karyawan'),
        ], string='Referensi')
    
    @api.one
    @api.depends('memorandum_ids.flag')
    def compute_flag(self):
        sp = self.env['hr_memorandum'].search([('nama_karyawan','=',self.id)]) or False
        if(sp):
            self.flag = sp.flag
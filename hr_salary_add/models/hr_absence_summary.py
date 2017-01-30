from openerp import models, fields, api, _
from openerp.exceptions import AccessError, Warning

import openerp.addons.decimal_precision as dp


class AbsenceSummary(models.Model):
    _name = "hr.absence.summary"
    
    employee_id = fields.Many2one("hr.employee", string="Nama Karyawan", required=True)
    jumlah_kehadiran = fields.Float(string="Jumlah Hari Kerja", required=True)
    periode = fields.Date(string="Tanggal", required=True, help="Tanggal ini akan diambil ke dalam perhitungan Periode sesuai dengan rules Periode dalam perhitungan Gaji")

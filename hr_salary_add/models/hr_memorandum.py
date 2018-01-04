from openerp import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools.misc import DEFAULT_SERVER_DATE_FORMAT
from openerp.addons.base.ir.ir_cron import _intervalTypes

class hr_memorandum(models.Model):
    _name = "hr_memorandum"
    
    name = fields.Char(string="Number")
    
    tanggal = fields.Date(string="Tanggal Pelanggaran", default=lambda self: fields.Date.context_today(self))
    nama_karyawan = fields.Many2one("hr.employee", string="Nama Karyawan", required=True)
    nama_atasan = fields.Many2one("hr.employee", string="Nama Atasan", required=True)
    jabatan = fields.Many2one('hr.job', string="Jabatan", compute="_compute_cabang")
    nama_cabang = fields.Many2one('hr.department', string="Nama Cabang", compute="_compute_cabang")
    alasan = fields.Text()
    flag = fields.Boolean(string="Status SP")
    type_id = fields.Many2one("hr.memorandum.type", string = "Type ID")
    date_from = fields.Date(default=lambda self: fields.Date.context_today(self))
    date_to = fields.Date(default=lambda self: fields.Date.context_today(self))
    lokasi = fields.Many2one('hr.department', string="Lokasi")
    state = fields.Selection([
            ('draft','Draft'),
            ('approve','Approve'),
            ('progres','Progres'),
            ('fault','Fault'),
            ('done','Done'),
        ], string='Status', default='draft')
    
    @api.multi
    def action_approve(self):
        self.name = self.env['ir.sequence'].get("memorandum")
        self.state = 'approve'

    @api.multi
    def action_accept(self):
        self.state = 'progres'
        employee = self.env['hr.employee'].search([('id','=',self.nama_karyawan.id)])
        employee.write({'flag':self.flag})
        
    @api.multi
    def action_fault(self):
        self.state = 'fault'
        
#     @api.onchange('nama_karyawan')
#     def onchange_cabang_asal(self):
#         if(self.nama_karyawan):
#             employee = self.env['hr.employee'].search([('id','=',self.nama_karyawan.id)])
#             self.nama_cabang = employee.department_id.id
#             self.jabatan = employee.job_id.id
            
    @api.one
    @api.depends('nama_karyawan')
    def _compute_cabang(self):
        employee = self.env['hr.employee'].search([('id','=',self.nama_karyawan.id)])
        self.nama_cabang = employee.department_id.id
        self.jabatan = employee.job_id.id
        self.nama_atasan = employee.parent_id.id
            
    @api.model
    def create(self, vals):
        employee = self.env['hr.employee'].search([('id','=',vals['nama_karyawan'])])
        vals['nama_cabang'] = employee.department_id.id
        vals['jabatan'] = employee.job_id.id
        return super(hr_memorandum, self).create(vals)
    
    @api.multi
    def write(self, vals):
        employee = self.env['hr.employee'].search([('id','=',vals.get('nama_karyawan'))])
        if(employee):
            vals['nama_cabang'] = employee.department_id.id
            vals['jabatan'] = employee.job_id.id
        return super(hr_memorandum, self).write(vals)

    @api.onchange('type_id')
    def _changes_type(self):
            if self.type_id:
                
                if not self.date_from: self.date_from = fields.Date.context_today(self)
                self.date_to = datetime.strptime(self.date_from, DEFAULT_SERVER_DATE_FORMAT) + _intervalTypes[self.type_id.interval_type](self.type_id.interval_number)

    def convert_roman(self,num):
        num_map = [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'), (100, 'C'), (90, 'XC'),
           (50, 'L'), (40, 'XL'), (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]
        roman = ''

        while num > 0:
            for i, r in num_map:
                while num >= i:
                    roman += r
                    num -= i

        return roman

    # def convert_date_indonesian(self,date_source):
    #     months_dict = {
    #         '01':"Januari",
    #         '02':"Februari",
    #         '03':"Maret",
    #         '04':"April",
    #         '05':"Mei",
    #         '06':"Juni",
    #         '07':"Juli",
    #         '08':"Agustus",
    #         '09':"September",
    #         '10':"Oktober",
    #         '11':"November",
    #         '12':"Desember",
    #         }
    #     if date_source:
    #         dt_source = datetime.strptime(date_source,'%Y-%m-%d')
    #         dt_return = dt_source.strftime('%Y')+months_dict.get(dt_source.strftime('%m'))+dt_source.strftime('%d')
    #         return dt_return 
    #     return '-'

    @api.multi
    def _get_date_parse(self,source_date,format,roman=False):
        datetime_source = datetime.strptime(source_date,'%Y-%m-%d %H:%M:%S')
        if roman:
            return self.convert_roman(int(datetime_source.strftime(format)))
        return datetime_source.strftime(format)

class hr_memorandum_type(models.Model):
    _name = "hr.memorandum.type"

    name = fields.Char(string="Nama")
    code = fields.Char(string="Code",size=8)
    interval_number = fields.Integer(string = "Interval Number" ,help="Repeat every x.")
    interval_type = fields.Selection( [('days', 'Hari'),('weeks', 'Minggu'), ('months', 'Bulan')], 'Interval Unit')

    
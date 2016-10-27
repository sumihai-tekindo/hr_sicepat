from openerp import models, fields, api

class hr_memorandum(models.Model):
    _name = "hr_memorandum"
    
    name = fields.Char(string="code", default=lambda self: self.env['ir.sequence'].get("memorandum"))
    
    tanggal = fields.Date(default=lambda self: fields.Date.context_today(self))
    nama_karyawan = fields.Many2one("hr.employee", string="Nama Karyawan", required=True)
    nama_atasan = fields.Many2one("hr.employee", string="Nama Atasan", required=True)
    jabatan = fields.Many2one('hr.job', string="Jabatan", compute="_compute_cabang")
    nama_cabang = fields.Many2one('hr.department', string="Nama Cabang", compute="_compute_cabang")
    alasan = fields.Text()
    flag = fields.Boolean(string="Status SP")
    
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
        employee = self.env['hr.employee'].search([('id','=',self.nama_karyawan.id)])
        employee.write({'flag':self.flag})
        
    @api.multi
    def action_reject(self):
        self.state = 'reject'
        
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
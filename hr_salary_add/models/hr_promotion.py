from openerp import models, fields, api

class hr_promotion(models.Model):
    _name = "hr_promotion"
    
    name = fields.Char(string="code", default=lambda self: self.env['ir.sequence'].get("promotion"))
    
    tanggal = fields.Date(default=lambda self: fields.Date.context_today(self))
    requestor = fields.Many2one('res.users', string="Requestor", default=lambda self: self.env.user)
    
    nama_karyawan = fields.Many2one("hr.employee", string="Nama Karyawan", required=True)
    jabatan_awal = fields.Many2one('hr.job', string="Jabatan Semula", readonly=True)
    cabang_awal = fields.Many2one('hr.department', string="Cabang Asal", readonly=True)
    usulan_jabatan_baru = fields.Many2one('hr.job', string="Usulan Jabatan", required=True)
    cabang_baru = fields.Many2one('hr.department', string="Cabang Baru", required=True)
    
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
        employee.write({'department_id':self.cabang_baru.id})
        employee.write({'job_id':self.usulan_jabatan_baru.id})
        
    @api.multi
    def action_reject(self):
        self.state = 'reject'
        
    @api.onchange('nama_karyawan')
    def onchange_cabang_asal(self):
        if(self.nama_karyawan):
            employee = self.env['hr.employee'].search([('id','=',self.nama_karyawan.id)])
            self.cabang_awal = employee.department_id.id
            self.jabatan_awal = employee.job_id.id
            
    @api.model
    def create(self, vals):
        employee = self.env['hr.employee'].search([('id','=',vals['nama_karyawan'])])
        vals['cabang_awal'] = employee.department_id.id
        vals['jabatan_awal'] = employee.job_id.id
        return super(hr_promotion, self).create(vals)
    
    @api.multi
    def write(self, vals):
        employee = self.env['hr.employee'].search([('id','=',vals.get('nama_karyawan'))])
        if(employee):
            vals['cabang_awal'] = employee.department_id.id
            vals['jabatan_awal'] = employee.job_id.id
        return super(hr_promotion, self).write(vals)
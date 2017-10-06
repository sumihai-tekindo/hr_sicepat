from openerp import models, fields, api
from openerp.exceptions import Warning

class emp_recruitment_level(models.Model):
    _name = "emp.recruitment.level"

    name = fields.Char(string="Nama")

class emp_recruitment_skill(models.Model):
    _name = "emp.recruitment.skill"

    name = fields.Char(string="Nama")

class emp_recruitment_bahasa(models.Model):
    _name = "emp.recruitment.bahasa"

    name = fields.Char(string="Nama")

class emp_recruitment_sumber(models.Model):
    _name = "emp.recruitment.sumber"

    name = fields.Char(string="Nama")

class emp_recruitment_agama(models.Model):
    _name = "emp.recruitment.agama"

    name = fields.Char(string="Nama")

class emp_recruitment_pendidikan(models.Model):
    _name = "emp.recruitment.pendidikan"

    name = fields.Char(string="Nama")

    
class emp_recruitment_req(models.Model):
    _name = "emp.recruitment.req"
    
    name = fields.Char(string="Number")
    user_id = fields.Many2one("res.users", string="Requestor")
    department = fields.Many2one('hr.department', string="Nama Departement", compute="_existing_employee")
    posisi = fields.Many2one('hr.job', string="Posisi", compute="_existing_employee")
    gaji_from = fields.Float(string="Gaji dari")
    gaji_to = fields.Float(string="Gaji sampai")
    tanggal = fields.Date(string="Tanggal Dibutuhkan", default=lambda self: fields.Date.context_today(self))
    jumlah = fields.Integer(sting="Jumlah di Butuhkan")
    analisa = fields.Text(string="Analisa Kebutuhan Karyawan")
    catatan = fields.Char(string="Catatan Khusus")
    deskripsi = fields.Text(string="Deskripsi Pekerjaan")
    usia_from = fields.Integer(string="Usia dari")
    usia_to = fields.Integer(string="Usia sampai")
    level_id = fields.Many2one("emp.recruitment.level", string = "Tingkat")
    skill_ids = fields.Many2many("emp.recruitment.skill", string = "Keahlian")
    bahasa_ids = fields.Many2many("emp.recruitment.bahasa", string = "bahasa")
    sumber_id = fields.Many2one("emp.recruitment.sumber", string = "Sumber Rekrutmen")
    agama_id = fields.Many2one("emp.recruitment.agama", string = "Agama")
    pendidikan_id = fields.Many2one("emp.recruitment.pendidikan", string = "Pendidikan")
    employee_ids = fields.Many2many("hr.employee", string="Karyawan yang sudah ada")
    
    description = fields.Char(string="Karena")
    employee_id = fields.Many2one("hr.employee", string="Nama Karyawan")
    permintaan = fields.Selection([
            ('replace','Mengganti Karyawan'),
            ('new','Penambahan Karyawan'),
            ('parttime','Kerja Waktu Tertentu'),
            ('other','Lainnya'),
        ],)

    keterangan = fields.Selection([
            ('resign','Mengundurkan Diri'),
            ('terminate','Diberhentikan')
        ],)

    status = fields.Selection([
            ('single','Single'),
            ('married','Married'),
            ('widower','Widower'),
            ('divorced','Divorced'),
        ],)
    
    skala = fields.Selection([
            ('1','1'),
            ('2','2'),
            ('3','2'),
            ('4','4'),
            ('5','5'),
            ('6','6'),
            ('7','7'),
            ('8','8'),
            ('9','9'),
            ('10','10'),
        ])

    pengalaman = fields.Selection([
            ('1','<1 Tahun'),
            ('2','1-2 Tahun'),
            ('3','2-3 Tahun'),
            ('4','>5 Tahun'),
        ])

    @api.one
    @api.depends('user_id')
    def _existing_employee(self):
        employee = self.env['hr.employee'].search([('id','=',self.user_id.id)])
        self.department = employee.department_id.id
        self.posisi = employee.job_id.id
            
    @api.model
    def create(self, vals):
        employee = self.env['hr.employee'].search([('id','=',vals['user_id'])])
        vals['department'] = employee.department_id.id
        vals['posisi'] = employee.job_id.id
        return super(emp_recruitment_req, self).create(vals)
    
    @api.multi
    def write(self, vals):
        employee = self.env['hr.employee'].search([('id','=',vals.get('user_id'))])
        if(employee):
            vals['department'] = employee.department_id.id
            vals['posisi'] = employee.job_id.id
        return super(emp_recruitment_req, self).write(vals)

    # @api.one
    # @api.depends('posisi')
    # def _existing_employee(self):
    #     employee_mgr_id = self.env['hr.employee'].search([('user_id','=',self.user_id.id)], limit=1)
    #     if not employee_mgr_id:
    #         raise Warning('Error')
    #     employee_ids = self.env['hr.employee'].search([('parent_id','=',self.employee_mgr_id.id)])


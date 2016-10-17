from openerp import models, fields, api
from openerp.osv import osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class hr_overtime(models.Model):
    _name = "hr_overtime"
    
    name = fields.Char(string="code", default=lambda self: self.env['ir.sequence'].get("overtime"))
    tanggal = fields.Date(default=lambda self: fields.Date.context_today(self))
    requestor = fields.Many2one('res.users', string="Requestor", default=lambda self: self.env.user)
    overtime_ids = fields.One2many('hr_overtime_line','overtime_id')
    
    state = fields.Selection([
            ('open','Open'),
            ('submit','Submit'),
            ('approved','Approved'),
            ('proses','Proses Di Gaji'),
            ('reject','Reject'),
        ], string='Status', default='open')
    
    @api.multi
    def action_submit(self):
        self.state = 'submit'

    @api.multi
    def action_approve(self):
        overtimes = self.env['hr_overtime_line'].search([('overtime_id','=',self.id)])
        status = False
        for overtime in overtimes:
            if(overtime.state=='draft'):
                status=True
        if(status==False):
            self.state = 'approved'
        else:
            raise osv.except_osv(_('Gagal Di Proses'), _('silahkan lakukan Approve atau Reject setiap lemburan'))
        
    @api.multi
    def action_reject(self):
        overtimes = self.env['hr_overtime_line'].search([('overtime_id','=',self.id)])
        status = False
        for overtime in overtimes:
            if(overtime.state=='draft'):
                status=True
        if(status==False):
            self.state = 'reject'
        else:
            raise osv.except_osv(_('Gagal Di Proses'), _('silahkan lakukan Approve atau Reject setiap lemburan'))
        
    @api.multi
    def action_proses(self):
        self.state = 'proses'

class hr_overtime_line(models.Model):
    _name = "hr_overtime_line"
    
    name = fields.Char(string="code")
    overtime_id = fields.Many2one('hr_overtime')
    nik = fields.Many2one("hr.employee", string="NIK", required=True)
    nilai = fields.Float(digits=dp.get_precision('Payroll'), string="Nilai", required=True)
    alasan = fields.Text()
    nama_cabang = fields.Many2one('account.analytic.account', string="Nama Cabang", required=True)
    state = fields.Selection([
            ('draft','Draft'),
            ('confirmed','Confirmed'),
            ('cancel','Cancel'),
        ], string='Status', default='draft')
    
    @api.multi
    def action_confirm(self):
        self.state = 'confirmed'
        
    @api.multi
    def action_cancel(self):
        self.state = 'cancel'
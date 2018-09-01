from openerp import models, fields, api, exceptions, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp import SUPERUSER_ID
from datetime import datetime

class EmailPayslipTest(models.TransientModel):
	_name = 'hr.payslip.email'

	def _get_active_ids(self):
		return self.env['hr.payslip'].browse(self._context.get('active_ids'))

	payslip_ids = fields.Many2many('hr.payslip', string='Payslip', required=True, default=_get_active_ids)

	@api.multi
	def send_via_email(self):
		self.ensure_one()
		
		if self.payslip_ids and len(self.payslip_ids) == 1:
			if not self.payslip_ids[0].employee_id.work_email:
				raise except_orm(_('No Email Defined!'),_("You must define email address for this employee!"))
			else:
				template = self.env.ref('hr_payslip_email.email_payslip_template')
				compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
				ctx = dict(
					default_model = 'hr.payslip',
					active_model = 'hr.payslip',
					model = 'hr.payslip',
					default_use_template = bool(template),
					default_template_id = template and template.id or False,
					composition_mode = 'comment',
					active_ids = [val.id for val in self.payslip_ids],
					active_id = self.payslip_ids[0].id,
					default_res_id = self.payslip_ids[0].id,
					res_id = self.payslip_ids[0].id,
				)
				return {
					'name': _('Compose Email for Payslip'),
					'type': 'ir.actions.act_window',
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'mail.compose.message',
					'src_model': 'hr.payslip',
					'views': [(compose_form.id, 'form')],
					'view_id': compose_form.id,
					'target': 'new',
					'context': ctx,
				}
		else:
			mail_message = self.env['mail.message']
			user = self.env['res.users'].browse(self._uid)
			import base64
			for payslip in self.payslip_ids:
				if not payslip.employee_id.work_email:
					mail_message.sudo().create({
							'subject': 'Notifikasi system email payslip',
							'author_id': SUPERUSER_ID,
							'date': datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
							'type': 'notification',
							'partner_ids': [(4, user.partner_id.id)],
							'body': 'Email untuk karyawan %s (%s) tidak terdefinisi' % (payslip.employee_id.name, payslip.employee_id.nik),
						})
				else:	
					template = self.env.ref('hr_payslip_email.email_payslip_template')
					ctx = dict(
						default_model = 'hr.payslip',
						active_model = 'hr.payslip',
						model = 'hr.payslip',
						default_use_template = bool(template),
						default_template_id = template and template.id or False,
						active_ids = [val.id for val in self.payslip_ids],
						active_id = payslip.id,
						default_res_id = payslip.id,
						res_id = payslip.id,
					)
					template.with_context(ctx).send_mail(payslip.id, force_send=True, raise_exception=True)

		return True


					

class HRPayslip(models.Model):
	_name = 'hr.payslip'
	_inherit = ['hr.payslip','mail.thread']

class ResCompany(models.Model):
	_inherit = 'res.company'

	hr_line_id = fields.Char(stirng="Line Id")
	hr_phone_contact = fields.Char(stirng="Contact Number")





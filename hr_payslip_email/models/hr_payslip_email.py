from openerp import models, fields, api, exceptions, _, tools
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

		ctx = dict(self._context)
		template = self.env.ref('hr_payslip_email.email_payslip_template')
		ctx.update({
			'default_model': 'hr.payslip',
			'active_model': 'hr.payslip',
			'model': 'hr.payslip',
			'default_use_template': bool(template),
			'default_template_id': template and template.id or False,
		})

		if self.payslip_ids and len(self.payslip_ids) == 1:
			if not self.payslip_ids[0].employee_id.work_email:
				raise except_orm(_('No Email Defined!'),_("You must define email address for this employee!"))
			else:
				compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
				birthday = self.payslip_ids[0].employee_id.birthday
				# set default password if birthday null
				payslip_password = self.payslip_ids[0].employee_id.nik
				if birthday:
					# 2 digit from each of the employee's birthday number
					payslip_password = ''.join(res[-2:] for res in birthday.split('-')[::-1])

				ctx.update({
					'composition_mode': 'comment',
					'active_ids': [self.payslip_ids[0].id],
					'active_id': self.payslip_ids[0].id,
					'default_res_id': self.payslip_ids[0].id,
					'res_id': self.payslip_ids[0].id,
					'set_password': payslip_password
				})

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
					birthday = payslip.employee_id.birthday
					# set default password if birthday null
					password = str(payslip.employee_id.nik)
					if birthday:
						# 2 digit from each of the employee's birthday number
						password = ''.join(res[-2:] for res in birthday.split('-')[::-1])

					ctx.update({
						'active_ids': [payslip.id],
						'active_id': payslip.id,
						'default_res_id': payslip.id,
						'res_id': payslip.id,
						'set_password': password
					})

					template.with_context(ctx).send_mail(payslip.id, force_send=True, raise_exception=True)

		return True

class HRPayslip(models.Model):
	_name = 'hr.payslip'
	_inherit = ['hr.payslip','mail.thread']

class ResCompany(models.Model):
	_inherit = 'res.company'

	hr_line_id = fields.Char(string="Line Id")
	hr_phone_contact = fields.Char(string="Contact Number")
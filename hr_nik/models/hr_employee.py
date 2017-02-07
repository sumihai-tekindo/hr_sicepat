# -*- coding: utf-8 -*-
# © 2011, 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import random
import string
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserWarning


class HrEmployee(models.Model):
    """Implement company wide unique identification number."""

    _inherit = 'hr.employee'

    nik = fields.Char(
        string='NIK',
        copy=False,
        readonly=False
    )

    _sql_constraints = [
        ('nik_uniq', 'unique(nik)',
         'The Employee Number must be unique across the company(s).'),
    ]
    
#   tambahan dari timotius untuk alamat ktp dan tanggal masuk  
    ktp_address_id = fields.Many2one('res.partner', string='KTP Adress')
    tgl_masuk = fields.Date(string='Tanggal Masuk', default=lambda self: fields.Date.context_today(self))
#   end

    @api.model
    def _generate_nik(self):
        """Generate a random employee identification number"""
        company = self.env.user.company_id
        employee_id = False
        if company.employee_id_gen_method == 'sequence':
            employee_id = self.env['ir.sequence'].get_id(company.employee_id_sequence.id)
        elif company.employee_id_gen_method == 'random':
            employee_id_random_digits = company.employee_id_random_digits
            tries = 0
            max_tries = 50
            while tries < max_tries:
                rnd = random.SystemRandom()
                employee_id = ''.join(rnd.choice(string.digits) for _ in xrange(employee_id_random_digits))
                if not self.search_count([('nik', '=', employee_id)]):
                    break
                tries += 1
            if tries == max_tries:
                raise UserWarning(_('Unable to generate an Employee ID number that is unique.'))
        return employee_id

    @api.model
    def create(self, vals):
        if not vals.get('nik'):
            ctx = dict(self._context, ir_sequence_date=vals.get('tgl_masuk', fields.Date.context_today(self)))
            eid = self.with_context(ctx)._generate_nik()
            vals['nik'] = eid
        return super(HrEmployee, self).create(vals)
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search(['|',('nik', '=', name),('name', '=', name)] + args, limit=limit)
        if not recs:
            recs = self.search(['|',('nik', operator, name),('name', operator, name)] + args, limit=limit)
        return recs.name_get()

    @api.multi
    def name_get(self):
        result = []
        for employee in self:
            name = employee.name_related or ''
            if employee.nik:
                name = "[%s] %s" % (employee.nik, name)
            result.append((employee.id, name))
        return result
# -*- coding: utf-8 -*-
import models
import wizard

def populate_jabatan_department_loan(cr, registry):
    cr.execute('UPDATE hr_loan '
               'SET jabatan_id = (SELECT job_id FROM hr_employee WHERE id=employee_id), '
               'department_id = (SELECT department_id FROM hr_employee WHERE id=employee_id) '
               'WHERE jabatan_id is NULL and department_id is NULL')

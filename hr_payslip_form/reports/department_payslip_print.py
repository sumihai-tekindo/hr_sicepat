# -*- encoding: utf-8 -*-
##############################################################################
#
#	OpenERP, Open Source Management Solution
#
#	Copyright (c) 2013 PT. SUMIHAI TEKNOLOGI INDONESIA. All rights reserved.
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU Affero General Public License as
#	published by the Free Software Foundation, either version 3 of the
#	License, or (at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU Affero General Public License for more details.
#
#	You should have received a copy of the GNU Affero General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import xlwt
import string
from xlwt import Formula as fm
from datetime import datetime
from openerp.osv import orm
from openerp.addons.report_xls.report_xls import report_xls
# from openerp.addons.report_xls.utils import rowcol_to_cell, _render

import time
from openerp.report import report_sxw
from openerp.tools.translate import translate
import logging

# from .nov_account_journal import nov_journal_print
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class department_payslip_xls_parser(report_sxw.rml_parse):

	def __init__(self, cr, uid, name, context):
		super(department_payslip_xls_parser, self).__init__(cr, uid, name,
														 context=context)
		self.context = context
		
		self.localcontext.update({
			'datetime': datetime,
			'get_by_dept':self._get_grouped_by_department,
			'get_by_job':self._get_grouped_by_job,
			'get_available_bank':self._get_available_bank,
			'get_by_dept_bank':self._get_by_dept_bank,
			'get_col_list':self._get_col_list,
		})

	def _get_grouped_by_department(self,data,objects):
		cr = self.cr
		uid = self.uid
		department_ids = self.pool.get('hr.department').search(cr,uid,[('id','in',data['department_ids'])],order="name asc")
		department_idsx = self.pool.get('hr.department').browse(cr,uid,department_ids)
		value = {}
		departments ={}
		for d in department_idsx:
			value.update({d.id:{}})
			departments.update({d.id:d.name})
		# iterate for every payslip
		for o in objects:
			e_dept_id = o.employee_id and o.employee_id.department_id and o.employee_id.department_id.id or False
			if e_dept_id:
				columns = ["DEPT","CLASS","EMP_COUNT","WORKDAYS_SUM","PACKAGES","BASIC","INSENTIF","TARGET","TBONUS","MEAL","BIKE","PERSISTANCE","NIGHT","OVERTIME","ALLOW","OTHER_ALL","LOAN","TOTAL"]
				dump_wd = {}
				for wd in o.worked_days_line_ids:
					dump_wd.update({
						wd.code:{
								'number_of_days':wd.number_of_days or 0.0,
								'number_of_hours':wd.number_of_hours  or 0.0,
								}
								})
				dump_sr ={}
				for sr in o.line_ids:
					dump_sr.update({
						sr.code : {
							'quantity':sr.quantity or 0.0,
							'rate':sr.rate or 0.0,
							'amount':sr.amount or 0.0,
							'total':sr.total or 0.0,
							}
						})

				curr = value.get(e_dept_id,{})
				DEPT = o.employee_id.department_id and o.employee_id.department_id.name or ""
				EMP_COUNT = curr.get('EMP_COUNT',0) + 1
				CLASS = ''
				WORKDAYS_SUM = curr.get('WORKDAYS_SUM',0.0) + (dump_wd.get('SISO',False) and dump_wd.get('SISO').get('number_of_days',0.0) or 0.0)
				PACKAGES = curr.get('PACKAGES',0.0) + (o.total_paket or 0.0)
				BASIC = curr.get('BASIC',0.0) + (dump_sr.get('BASIC',False) and dump_sr.get('BASIC').get('total',0.0) or 0.0)
				INSENTIF = curr.get('INSENTIF',0.0) + (dump_sr.get('INSENTIF',False) and dump_sr.get('INSENTIF').get('total',0.0) or 0.0)
				TARGET = curr.get('TARGET',0.0) + (dump_sr.get('TARGET',False) and dump_sr.get('TARGET').get('total',0.0) or 0.0)
				TBONUS = curr.get('TBONUS',0.0) + (dump_sr.get('TBONUS',False) and dump_sr.get('TBONUS').get('total',0.0) or 0.0)
				MEAL = curr.get('MEAL',0.0) + (dump_sr.get('MEAL',False) and dump_sr.get('MEAL').get('total',0.0) or 0.0)
				BIKE = curr.get('BIKE',0.0) + (dump_sr.get('BIKE',False) and dump_sr.get('BIKE').get('total',0.0) or 0.0)
				PERSISTANCE = curr.get('PERSISTANCE',0.0) + (dump_sr.get('PERSISTANCE',False) and dump_sr.get('PERSISTANCE').get('total',0.0) or 0.0)
				NIGHT = curr.get('NIGHT',0.0) + 0.0
				OVERTIME = curr.get('OVERTIME',0.0) + (dump_sr.get('OVERTIME',False) and dump_sr.get('OVERTIME').get('total',0.0) or 0.0)
				ALLOW = curr.get('ALLOW',0.0) + (dump_sr.get('ALLOW',False) and dump_sr.get('ALLOW').get('total',0.0) or 0.0)
				OTHER_ALL = curr.get('OTHER_ALL',0.0) + 0.0
				LOAN = curr.get('LOAN',0.0) + (dump_sr.get('LOAN',False) and dump_sr.get('LOAN').get('total',0.0) or 0.0)
				TOTAL = curr.get('TOTAL',0.0) + (dump_sr.get('NET',False) and dump_sr.get('NET').get('total',0.0) or 0.0)
				for col in columns:
					curr.update({col:eval(col)})
				value.update({e_dept_id:curr})
			else:
				continue
		return departments,value

	def _get_grouped_by_job(self,data,objects):
		cr = self.cr
		uid = self.uid
		department_ids = self.pool.get('hr.department').search(cr,uid,[('id','in',data['department_ids'])],order="name asc")
		job_ids = self.pool.get('hr.job').search(cr,uid,[],order="name asc")
		job_idsx = self.pool.get('hr.job').browse(cr,uid,job_ids)
		value = {}
		jobs ={}
		for j in job_idsx:
			value.update({j.id:{}})
			jobs.update({j.id:j.name})

		# iterate for every payslip
		for o in objects:
			e_job_id = o.employee_id and o.employee_id.job_id and o.employee_id.job_id.id or False
			if e_job_id:
				columns = ["JOB","EMP_COUNT","WORKDAYS_SUM","PACKAGES","BASIC","INSENTIF_TYPE","INSENTIF","TBONUS","MEAL","BIKE","PERSISTANCE","NIGHT","OVERTIME","ALLOW","OTHER_ALL","LOAN","TOTAL"]
				dump_wd = {}
				for wd in o.worked_days_line_ids:
					dump_wd.update({
						wd.code:{
								'number_of_days':wd.number_of_days or 0.0,
								'number_of_hours':wd.number_of_hours  or 0.0,
								}
								})
				dump_sr ={}
				for sr in o.line_ids:
					dump_sr.update({
						sr.code : {
							'quantity':sr.quantity or 0.0,
							'rate':sr.rate or 0.0,
							'amount':sr.amount or 0.0,
							'total':sr.total or 0.0,
							}
						})

				curr = value.get(e_job_id,{})

				JOB = o.employee_id.job_id and o.employee_id.job_id.name or ""
				EMP_COUNT = curr.get('EMP_COUNT',0) + 1
				WORKDAYS_SUM = curr.get('WORKDAYS_SUM',0.0) + (dump_wd.get('SISO',False) and dump_wd.get('SISO').get('number_of_days',0.0) or 0.0)
				PACKAGES = curr.get('PACKAGES',0.0) + (o.total_paket or 0.0)
				BASIC = curr.get('BASIC',0.0) + (dump_sr.get('BASIC',False) and dump_sr.get('BASIC').get('total',0.0) or 0.0)
				INSENTIF_TYPE = ''
				INSENTIF = curr.get('INSENTIF',0.0) + (dump_sr.get('INSENTIF',False) and dump_sr.get('INSENTIF').get('total',0.0) or 0.0)
				TBONUS = curr.get('TBONUS',0.0) + (dump_sr.get('TBONUS',False) and dump_sr.get('TBONUS').get('total',0.0) or 0.0)
				MEAL = curr.get('MEAL',0.0) + (dump_sr.get('MEAL',False) and dump_sr.get('MEAL').get('total',0.0) or 0.0)
				BIKE = curr.get('BIKE',0.0) + (dump_sr.get('BIKE',False) and dump_sr.get('BIKE').get('total',0.0) or 0.0)
				PERSISTANCE = curr.get('PERSISTANCE',0.0) + (dump_sr.get('PERSISTANCE',False) and dump_sr.get('PERSISTANCE').get('total',0.0) or 0.0)
				NIGHT = curr.get('NIGHT',0.0) + 0.0
				OVERTIME = curr.get('OVERTIME',0.0) + (dump_sr.get('OVERTIME',False) and dump_sr.get('OVERTIME').get('total',0.0) or 0.0)
				ALLOW = curr.get('ALLOW',0.0) + (dump_sr.get('ALLOW',False) and dump_sr.get('ALLOW').get('total',0.0) or 0.0)
				OTHER_ALL = curr.get('OTHER_ALL',0.0) + 0.0
				LOAN = curr.get('LOAN',0.0) + (dump_sr.get('LOAN',False) and dump_sr.get('LOAN').get('total',0.0) or 0.0)
				DEDUCT = curr.get('DEDUCT',0.0) + (dump_sr.get('DEDUCT',False) and dump_sr.get('DEDUCT').get('total',0.0) or 0.0)
				TOTAL= curr.get('TOTAL',0.0) + (dump_sr.get('NET',False) and dump_sr.get('NET').get('total',0.0) or 0.0)
				for col in columns:
					curr.update({col:eval(col)})
				value.update({e_job_id:curr})
			else:
				continue
		return jobs,value

	def _get_available_bank(self,objects):
		banks = {}
		for o in objects:
			if o.employee_id and o.employee_id.bank_account_id and o.employee_id.bank_account_id.bank and o.employee_id.bank_account_id.bank.id:
				banks.update({o.employee_id.bank_account_id.bank.id:o.employee_id.bank_account_id.bank.name})
		return banks

	def _get_col_list(self):
		def get_string(val):
			return string.uppercase[val%26]*(val / 26+1)

		col_list=list()
		for i in range(-1, 26):
			for j in range(0, 26):
				if i==-1:
					col_list.append(str(get_string(j)))
				else:
					col_list.append(str(get_string(i) + get_string(j)))
		return col_list

	def _get_by_dept_bank(self,data,objects):
		banks = self._get_available_bank(objects)
		cr = self.cr
		uid = self.uid
		department_ids = self.pool.get('hr.department').search(cr,uid,[('id','in',data['department_ids'])],order="name asc")
		department_idsx = self.pool.get('hr.department').browse(cr,uid,department_ids)
		value = {}
		columns = ["DEPT","TOTAL"]
		for b in banks:
			columns.append(str(b))
		departments ={}
		for d in department_idsx:
			value.update({d.id:{}})
			departments.update({d.id:d.name})
		# iterate for every payslip
		for o in objects:
			e_dept_id = o.employee_id and o.employee_id.department_id and o.employee_id.department_id.id or False
			e_bank_id = o.employee_id and o.employee_id.bank_account_id and o.employee_id.bank_account_id.bank and o.employee_id.bank_account_id.bank.id or False
			if e_dept_id and e_bank_id:
				dump_wd = {}
				for wd in o.worked_days_line_ids:
					dump_wd.update({
						wd.code:{
								'number_of_days':wd.number_of_days or 0.0,
								'number_of_hours':wd.number_of_hours  or 0.0,
								}
								})
				dump_sr ={}
				for sr in o.line_ids:
					dump_sr.update({
						sr.code : {
							'quantity':sr.quantity or 0.0,
							'rate':sr.rate or 0.0,
							'amount':sr.amount or 0.0,
							'total':sr.total or 0.0,
							}
						})
				curr = value.get(e_dept_id,{})
				curr_bank = curr.get(e_bank_id,0.0)
				O_NET = (dump_sr.get('NET',False) and dump_sr.get('NET').get('total',0.0) or 0.0)
				TOTAL = curr.get('TOTAL',0.0) + O_NET
				DEPT = o.employee_id and o.employee_id.department_id and o.employee_id.department_id.name or ''
				for col in ["DEPT","TOTAL"]:
					curr.update({col:eval(col)})
				curr.update({e_bank_id:curr_bank + O_NET})
				value.update({e_dept_id:curr})
			else:
				continue
		return departments,value


class department_payslip_xls(report_xls):

	def __init__(self, name, table, rml=False, parser=False, header=True,
				 store=False):
		super(department_payslip_xls, self).__init__(
			name, table, rml, parser, header, store)


	def generate_xls_report(self, _p, _xs, data, objects, wb):
		##Penempatan untuk template rows
		title_style 					= xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz left; ')
		title_style_center				= xlwt.easyxf('font: height 220, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz center; ')
		normal_style 					= xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz left;',num_format_str='#,##0.00;-#,##0.00')
		normal_style_center				= xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center;')
		normal_style_float 				= xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz right;',num_format_str='#,##0.00;-#,##0.00')
		normal_style_float_round 		= xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz right;',num_format_str='#,##0')
		normal_style_float_bold 		= xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz right;',num_format_str='#,##0.00;-#,##0.00')
		normal_bold_style 				= xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz left; ')
		normal_bold_style_a 			= xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz left; ')
		normal_bold_style_b 			= xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on;pattern: pattern solid, fore_color gray25; align: wrap on, vert centre, horiz left; ')
		th_top_style 					= xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center; border:top thick')
		th_both_style_left 				= xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz left;')
		th_both_style 					= xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center; border:top thick, bottom thick')
		th_bottom_style 				= xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center; border:bottom thick')
		th_both_style_dashed 			= xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center; border:top thick, bottom dashed',num_format_str='#,##0.00;-#,##0.00')
		th_both_style_dashed_bottom 	= xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz right; border:bottom dashed',num_format_str='#,##0.00;-#,##0.00')
		
		subtotal_title_style			= xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz left; borders: top thin, bottom thin;')
		subtotal_style				  	= xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz right; borders: bottom thin;',num_format_str='#,##0;-#,##0')
		subtotal_style2				 	= xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz right; borders: top thin, bottom thin;',num_format_str='#,##0.00;-#,##0.00')
		total_title_style			   	= xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz left;pattern: pattern solid, fore_color gray25; borders: top thin, bottom thin;')
		total_style					 	= xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz right;pattern: pattern solid, fore_color gray25; borders: top thin, bottom thin;',num_format_str='#,##0.0000;(#,##0.0000)')
		total_style2					= xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz right;pattern: pattern solid, fore_color gray25; borders: top thin, bottom thin;',num_format_str='#,##0.00;(#,##0.00)')
		subtittle_top_and_bottom_style  = xlwt.easyxf('font: height 240, name Times New Roman, colour_index black, bold off, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color white;')
		
		normal_style_float_round_total 	= xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz right; borders: top thin, bottom thin;',num_format_str='#,##0')

		if data['t_report']=='department':
			ws = wb.add_sheet("Payslip")
			ws.panes_frozen = True
			ws.remove_splits = True
			ws.portrait = 0  # Landscape
			ws.fit_width_to_pages = 1
			ws.preview_magn = 100
			ws.normal_magn = 100
			ws.print_scaling=100
			ws.page_preview = False
			ws.set_fit_width_to_pages(1)
			
			ws.write_merge(0,0,0,19,"REKAPITULASI PAYSLIP PER EMPLOYEE",title_style_center)
			ws.write(3,0,"PERIODE",normal_bold_style_a)
			ws.write_merge(3,3,1,4,": "+data['start_date']+" - "+data['end_date'],normal_bold_style_a)
			ws.write(4,0,"WILAYAH",normal_bold_style_a)
			ws.write_merge(4,4,1,4,": "+data['department_name'],normal_bold_style_a)
			headers = ["NO","CABANG","NIK","NAMA","JENIS KELAMIN","STATUS","TANGGUNGAN","NPWP","ALAMAT KTP","BANK","NO REKENING","POSISI","TGL.MASUK KERJA","HARI KERJA","PAKET","GAJI POKOK",
					"UANG MAKAN","UANG TRANSPORT","KERAJINAN","BONUS PAKET 1","BONUS PAKET 2","INSENTIF","TUNJANGAN OPERASIONAL",
					"TUNJANGAN JABATAN","SERVICE MOTOR","LEMBURAN","PINJAMAN","POTONGAN HP","POTONGAN BARANG","POTONGAN LAIN","BPJS KES","BPJS JHT","GROSS","DEDUCTION","THP","KETERANGAN",
					]
			available_banks = _p.get_available_bank (objects)
			for bank in available_banks:
				headers.append(bank)

			headers.append("TUNAI") #Tambahan Headers

			col_pos = 0
			for head in headers :

				ws.write(6,col_pos,head,th_top_style)
				col_pos+=1
			row_pos = 7
			
			columns = ["NO","CABANG","NIK","NAMA","JEN_KEL","MARITAL","TANGGUNGAN","NPWP","ALAMAT","BANK","NO_REK","POS","TGL_MSK","WORKDAYS","PAKET","BASIC","MEAL","TRANSPORT",
					"PERSISTANCE","TARGET","TBONUS","INSENTIF","OPER","ALLOW","BIKE","OVERTIME","LOAN","POTHP","POTBRG","POTLL","BPJS_KES","BPJS_JHT","GROSS","DEDUCT","TOTAL","KETERANGAN"]
			for bank in available_banks:
				columns.append(bank)

			columns.append("TUNAI")

			counter=1
			
			col_pos=0
			for o in objects:								#hr.payslip
				dump_wd = {}
				for wd in o.worked_days_line_ids:
					dump_wd.update({
						wd.code:{
								'number_of_days':wd.number_of_days or 0.0,
								'number_of_hours':wd.number_of_hours  or 0.0,
								}
								})
				dump_sr ={}										
				for sr in o.line_ids:
					dump_sr.update({
						sr.code : {
							'quantity':sr.quantity or 0.0,
							'rate':sr.rate or 0.0,
							'amount':sr.amount or 0.0,
							'total':sr.total or 0.0,
							'keterangan':sr.note_pinjaman,
							}
						})	
				
				
				
				
				
				NO = str(counter)
				CABANG = o.employee_id.department_id.name or 'Undefined'
				NIK = o.employee_id.nik or ''
				NAMA = o.employee_id.name or 'Undefined'
				JEN_KEL = o.employee_id.gender or ''
				MARITAL = o.employee_id.marital or '-'
				TANGGUNGAN = o.employee_id.children or 0
				NPWP = o.employee_id.no_npwp or '-'
				ALAMAT = o.employee_id.ktp_address_id and o.employee_id.ktp_address_id.contact_address or ''
				BANK = o.employee_id.bank_account_id.bank_name or 'Undefined'
				NO_REK = o.employee_id.bank_account_id.acc_number or 'Undefined'
				POS = o.employee_id.job_id and o.employee_id.job_id.name or 'Undefined'
				TGL_MSK = o.employee_id and o.employee_id.tgl_masuk or ''
				WORKDAYS = dump_wd.get('SISO',False) and dump_wd.get('SISO').get('number_of_days',0.0) or 0.0
				PAKET = o.total_paket or 0.0
				BASIC = dump_sr.get('BASIC',False) and dump_sr.get('BASIC').get('total',0.0) or 0.0
				MEAL = dump_sr.get('MEAL',False) and dump_sr.get('MEAL').get('total',0.0) or 0.0
				TRANSPORT = dump_sr.get('TRANSPORT',False) and dump_sr.get('TRANSPORT').get('total',0.0) or 0.0
				PERSISTANCE = dump_sr.get('PERSISTANCE',False) and dump_sr.get('PERSISTANCE').get('total',0.0) or 0.0
				TARGET = dump_sr.get('TARGET',False) and dump_sr.get('TARGET').get('total',0.0) or 0.0
				TBONUS = dump_sr.get('TBONUS',False) and dump_sr.get('TBONUS').get('total',0.0) or 0.0
				INSENTIF = dump_sr.get('INSENTIF',False) and dump_sr.get('INSENTIF').get('total',0.0) or 0.0
				OPER = dump_sr.get('OPER',False) and dump_sr.get('OPER').get('total',0.0) or 0.0
				ALLOW = dump_sr.get('ALLOW',False) and dump_sr.get('ALLOW').get('total',0.0) or 0.0
				BIKE = dump_sr.get('BIKE',False) and dump_sr.get('BIKE').get('total',0.0) or 0.0
				OVERTIME = dump_sr.get('OVERTIME',False) and dump_sr.get('OVERTIME').get('total',0.0) or 0.0
				LOAN = dump_sr.get('LOAN',False) and dump_sr.get('LOAN').get('total',0.0) or 0.0
				POTHP = dump_sr.get('POTHP',False) and dump_sr.get('POTHP').get('total',0.0) or 0.0
				POTBRG = dump_sr.get('POTBRG',False) and dump_sr.get('POTBRG').get('total',0.0) or 0.0
				POTLL = dump_sr.get('POTLL',False) and dump_sr.get('POTLL').get('total',0.0) or 0.0
				BPJS_KES = dump_sr.get('PJK_EMP',False) and dump_sr.get('PJK_EMP').get('total',0.0) or 0.0
				BPJS_JHT = dump_sr.get('JHT_EMP',False) and dump_sr.get('JHT_EMP').get('total',0.0) or 0.0
				GROSS = dump_sr.get('GROSS',False) and dump_sr.get('GROSS').get('total',0.0) or 0.0
				DEDUCT = 0.0
				TOTAL = dump_sr.get('NET',False) and dump_sr.get('NET').get('total',0.0) or 0.0
 				
				KETERANGAN = ""
 				KETERANGAN += (dump_sr.get('LOAN',False) and dump_sr.get('LOAN').get('keterangan',False)) or ""
 				KETERANGAN += (dump_sr.get('POTHP',False) and dump_sr.get('POTHP').get('keterangan',False)) or ""
 				KETERANGAN += (dump_sr.get('POTBRG',False) and dump_sr.get('POTBRG').get('keterangan',False)) or ""
				TUNAI = 0.0
				col_pos = 0

				for colx in columns:
					
					ws.write(row_pos,col_pos,eval(str(colx)),normal_style_float_round)
					col_pos+=1

				counter+=1
				row_pos+=1

			ws.write_merge(row_pos,row_pos,1,5,"TOTAL",title_style)
			
			col_list = _p.get_col_list()
			for i in range(6,len(columns)):
				chr_ord = col_list[i]
				ws.write(row_pos,i,xlwt.Formula("SUM($"+chr_ord+"$8:$"+chr_ord+"$"+str(row_pos)+")"),normal_style_float_round_total)


		elif data['t_report']=='all':
			ws = wb.add_sheet('REGIONAL BASED')
			ws.panes_frozen = True
			ws.remove_splits = True
			ws.portrait = 0  # Landscape
			ws.fit_width_to_pages = 1
			ws.preview_magn = 100
			ws.normal_magn = 100
			ws.print_scaling=100
			ws.page_preview = False
			ws.set_fit_width_to_pages(1)

			ws.write_merge(0,0,0,19,"REKAPITULASI PAYSLIP DEPARTMENT",title_style_center)
			ws.write(3,0,"PERIODE",normal_bold_style_a)
			ws.write_merge(3,3,1,4,": "+data['start_date']+" - "+data['end_date'],normal_bold_style_a)
			headers = ["NO","DAERAH","KLASIFIKASI (CABANG/GERAI/TOKO)","JUMLAH KARYAWAN","JUMLAH HARI KERJA BULAN INI","JUMLAH PAKET","GAJI POKOK","INSENTIF","BONUS PAKET 1","BONUS PAKET 2","U.MAKAN","SERVICE MOTOR","U.KERAJINAN(all)","T.K MALAM","LEMBURAN","TUNJANGAN JABATAN","TUNJANGAN LAIN-LAIN","HUTANG PINJAMAN","POTONGAN","TOTAL"]		
			columns = ["NO","DEPT","CLASS","EMP_COUNT","WORKDAYS_SUM","PACKAGES","BASIC","INSENTIF","TARGET","TBONUS","MEAL","BIKE","PERSISTANCE","NIGHT","OVERTIME","ALLOW","OTHER_ALL","LOAN","DEDUCT","TOTAL"]
			
			departments,grouped_objects = _p.get_by_dept(data,objects)
			# print "======grouped_objects=========",grouped_objects
			col_pos=0
			for head in headers :
				ws.write(6,col_pos,head,th_top_style)
				col_pos+=1
			col_pos = 0
			row_pos = 7 
			NO = 1
			for group in departments:
				col_pos = 0
				for colx in columns:
					if col_pos == 0:
						ws.write(row_pos,col_pos,int(eval(colx)),normal_style_center)
					else:
						if grouped_objects.get(group,False):
							if grouped_objects.get(group,False).get(colx,False):
								ws.write(row_pos,col_pos,grouped_objects.get(group).get(colx),normal_style)
					col_pos+=1
				NO+=1
				row_pos+=1
			ws.write_merge(row_pos,row_pos,1,2,"TOTAL",title_style)
			
			for i in range(3,len(columns)):
				chr_ord =chr(ord('A') + i)
				ws.write(row_pos,i,xlwt.Formula("SUM($"+chr_ord+"$8:$"+chr_ord+"$"+str(row_pos)+")"),title_style)
		elif data['t_report']=='totalled':
			ws = wb.add_sheet('TOTALLED PER BANK')
			ws.panes_frozen = True
			ws.remove_splits = True
			ws.portrait = 0  # Landscape
			ws.fit_width_to_pages = 1
			ws.preview_magn = 100
			ws.normal_magn = 100
			ws.print_scaling=100
			ws.page_preview = False
			ws.set_fit_width_to_pages(1)

			available_banks = _p.get_available_bank(objects)
			headers = ["NO","WILAYAH","TOTAL"]		
			columns = ["NO","DEPT","TOTAL"]
			for b in available_banks:
				headers.append(available_banks.get(b))
				columns.append(b)
			ws.write_merge(0,0,0,3+len(available_banks),"REKAPITULASI PAYSLIP PER DEPARTMENT PER BANK",title_style_center)
			ws.write(3,0,"PERIODE",normal_bold_style_a)
			ws.write_merge(3,3,1,4,": "+data['start_date']+" - "+data['end_date'],normal_bold_style_a)
			dept,grouped_objects = _p.get_by_dept_bank(data,objects)

			col_pos=0
			for head in headers :
				ws.write(6,col_pos,head,th_top_style)
				col_pos+=1
			col_pos = 0
			row_pos = 7 
			NO = 1
			for group in dept:
				col_pos = 0
				for colx in columns:
					if col_pos == 0:
						ws.write(row_pos,col_pos,int(eval(colx)),normal_style_center)
					else:
						if grouped_objects.get(group,False):
							if grouped_objects.get(group,False).get(colx,False):
								ws.write(row_pos,col_pos,grouped_objects.get(group).get(colx),normal_style)
					col_pos+=1
				NO+=1
				row_pos+=1
			ws.write_merge(row_pos,row_pos,0,1,"TOTAL",title_style)
			
			for i in range(2,len(columns)):
				chr_ord =chr(ord('A') + i)
				ws.write(row_pos,i,xlwt.Formula("SUM($"+chr_ord+"$8:$"+chr_ord+"$"+str(row_pos)+")"),title_style)
		else:
			ws = wb.add_sheet('JOB POSITION BASED')
			ws.panes_frozen = True
			ws.remove_splits = True
			ws.portrait = 0  # Landscape
			ws.fit_width_to_pages = 1
			ws.preview_magn = 100
			ws.normal_magn = 100
			ws.print_scaling=100
			ws.page_preview = False
			ws.set_fit_width_to_pages(1)

			ws.write_merge(0,0,0,19,"REKAPITULASI PAYSLIP PER JOB POSITION",title_style_center)
			ws.write(3,0,"PERIODE",normal_bold_style_a)
			ws.write_merge(3,3,1,4,": "+data['start_date']+" - "+data['end_date'],normal_bold_style_a)

			headers = ["NO","POSISI / JABATAN","JUMLAH KARYAWAN","JUMLAH HARI KERJA BULAN INI","JUMLAH PAKET","GAJI POKOK","TIPE INSENTIF","NILAI INSENTIF","BONUS PAKET 2","U.MAKAN","SERVICE MOTOR","U.KERAJINAN(all)","T.K MALAM","LEMBURAN","TUNJANGAN JABATAN","TUNJANGAN LAIN-LAIN","HUTANG PINJAMAN","POTONGAN","TOTAL"]		
			columns = ["NO","JOB","EMP_COUNT","WORKDAYS_SUM","PACKAGES","BASIC","INSENTIF_TYPE","INSENTIF","TBONUS","MEAL","BIKE","PERSISTANCE","NIGHT","OVERTIME","ALLOW","OTHER_ALL","LOAN","DEDUCT","TOTAL"]
						
			jobs,grouped_objects = _p.get_by_job(data,objects)
			col_pos=0
			for head in headers :
				ws.write(6,col_pos,head,th_top_style)
				col_pos+=1
			NO = 1

			row_pos = 7 

			for group in jobs:
				col_pos = 0
				for colx in columns:
					if col_pos == 0 and grouped_objects.get(group,False):
						ws.write(row_pos,col_pos,int(eval(colx)),normal_style_center)
						col_pos+=1
					else:
						if grouped_objects.get(group,False):
							# print "=========>",colx,grouped_objects.get(group,False).get(colx,False)
							if grouped_objects.get(group,False).get(colx,False):
								ws.write(row_pos,col_pos,grouped_objects.get(group).get(colx),normal_style)
						col_pos+=1
				if grouped_objects.get(group,False):
					NO+=1
					row_pos+=1

			ws.write_merge(row_pos,row_pos,0,1,"TOTAL",title_style)
			
			for i in range(2,len(columns)):
				chr_ord =chr(ord('A') + i)
				ws.write(row_pos,i,xlwt.Formula("SUM($"+chr_ord+"$8:$"+chr_ord+"$"+str(row_pos)+")"),title_style)


department_payslip_xls('report.department.payslip.report.xls', 'hr.payslip',
					parser=department_payslip_xls_parser)
department_payslip_xls('report.all.payslip.report.xls', 'hr.payslip',
					parser=department_payslip_xls_parser)
department_payslip_xls('report.functional.payslip.report.xls', 'hr.payslip',
					parser=department_payslip_xls_parser)
department_payslip_xls('report.totalled.payslip.report.xls', 'hr.payslip',
					parser=department_payslip_xls_parser)
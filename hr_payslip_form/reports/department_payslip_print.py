# -*- encoding: utf-8 -*-
##############################################################################
#
#	OpenERP, Open Source Management Solution
#
#	Copyright (c) 2013 Noviat nv/sa (www.noviat.com). All rights reserved.
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
		})


class department_payslip_xls(report_xls):

	def __init__(self, name, table, rml=False, parser=False, header=True,
				 store=False):
		super(department_payslip_xls, self).__init__(
			name, table, rml, parser, header, store)


	def generate_xls_report(self, _p, _xs, data, objects, wb):
		print "objects==============",objects
		print "=====================",data
		ws = wb.add_sheet(data['department_name'])
		ws.panes_frozen = True
		ws.remove_splits = True
		ws.portrait = 0  # Landscape
		ws.fit_width_to_pages = 1
		ws.preview_magn = 100
		ws.normal_magn = 100
		ws.print_scaling=100
		ws.page_preview = False
		ws.set_fit_width_to_pages(1)
		
		
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
		
		ws.write_merge(0,0,0,19,"REKAPITULASI PAYSLIP DEPARTMENT",title_style_center)
		ws.write(3,0,"PERIODE",normal_bold_style_a)
		ws.write_merge(3,3,1,4,": "+data['start_date']+" - "+data['end_date'],normal_bold_style_a)
		ws.write(4,0,"WILAYAH",normal_bold_style_a)
		ws.write_merge(4,4,1,4,": "+data['department_name'],normal_bold_style_a)
		headers = ["NO","NAMA","POSISI","TGL.MASUK KERJA","HARI KERJA","PAKET","BASIC","MEAL","TRANSPORT","PERSISTANCE","TARGET","TBONUS","INSENTIF","OPER","ALLOW","BIKE","OVERTIME","LOAN"]
		col_pos=0
		for head in headers :
			ws.write(6,col_pos,head,th_top_style)
			col_pos+=1

		row_pos = 7
		
		columns = ["NO","NAMA","POS","TGL_MSK","WORKDAYS","PAKET","BASIC","MEAL","TRANSPORT","PERSISTANCE","TARGET","TBONUS","INSENTIF","OPER","ALLOW","BIKE","OVERTIME","LOAN"]
		counter=1
		for o in objects:
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

			NO = str(counter)
			NAMA = o.employee_id.name or 'Undefined'
			POS = o.employee_id.job_id and o.employee_id.job_id.name or 'Undefined'
			TGL_MSK = ''
			WORKDAYS = dump_wd.get('SISO',0.0).get('number_of_days',0.0) or 0.0
			PAKET = ''
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
			col_pos = 0
			for colx in columns:
				ws.write(row_pos,col_pos,eval(colx),normal_style)
				col_pos+=1
			counter+=1
			row_pos+=1
			

department_payslip_xls('report.department.payslip.report.xls', 'hr.payslip',
					parser=department_payslip_xls_parser)

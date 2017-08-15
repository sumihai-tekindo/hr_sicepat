from openerp import models, fields, api
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import datetime

# from openerp import SUPERUSER_ID, api

class stock_transfer_details(models.TransientModel):
	_inherit = "stock.transfer_details"
	
	def default_get(self, cr, uid, fields, context=None):
		if context is None: context = {}
		res = super(stock_transfer_details, self).default_get(cr, uid, fields, context=context)
		if res and res.get('item_ids',False):
			picking_ids = context.get('active_ids', [])
			active_model = context.get('active_model')

			if not picking_ids or len(picking_ids) != 1:
				# Partial Picking Processing may only be done for one picking at a time
				return res
			assert active_model in ('stock.picking'), 'Bad context propagation'
			picking_id, = picking_ids
			picking = self.pool.get('stock.picking').browse(cr, uid, picking_id, context=context)
			items = []
			packs = []
			
			account_analytic_id = picking.move_lines and picking.move_lines[0].account_analytic_id and picking.move_lines[0].account_analytic_id.id or False
			account_analytic_dest_id = picking.move_lines and picking.move_lines[0].account_analytic_dest_id and picking.move_lines[0].account_analytic_dest_id.id or False

			for op in picking.pack_operation_ids:
				
				item = {
					'packop_id': op.id,
					'product_id': op.product_id.id,
					'product_uom_id': op.product_uom_id.id,
					'quantity': op.product_qty,
					'package_id': op.package_id.id,
					'lot_id': op.lot_id.id,
					'sourceloc_id': op.location_id.id,
					'destinationloc_id': op.location_dest_id.id,
					'result_package_id': op.result_package_id.id,
					'date': op.date,
					'owner_id': op.owner_id.id,
					'account_analytic_id':account_analytic_id,
					'account_analytic_dest_id':account_analytic_dest_id,

				}
				if op.product_id:
					items.append(item)
				elif op.package_id:
					packs.append(item)
			res.update(item_ids=items)
			res.update(packop_ids=packs)
		return res

	@api.one
	def do_detailed_transfer(self):
		if self.picking_id.state not in ['assigned', 'partially_available']:
			raise Warning(_('You cannot transfer a picking in state \'%s\'.') % self.picking_id.state)

		processed_ids = []
		# Create new and update existing pack operations
		move_ids = [x.id for x in self.picking_id.move_lines]
		for lstits in [self.item_ids, self.packop_ids]:
			for prod in lstits:
				pack_datas = {
					'product_id': prod.product_id.id,
					'product_uom_id': prod.product_uom_id.id,
					'product_qty': prod.quantity,
					'package_id': prod.package_id.id,
					'lot_id': prod.lot_id.id,
					'location_id': prod.sourceloc_id.id,
					'location_dest_id': prod.destinationloc_id.id,
					'result_package_id': prod.result_package_id.id,
					'date': prod.date if prod.date else datetime.now(),
					'owner_id': prod.owner_id.id,
				}
				if prod.packop_id:
					prod.packop_id.with_context(no_recompute=True).write(pack_datas)
					processed_ids.append(prod.packop_id.id)
				else:
					pack_datas['picking_id'] = self.picking_id.id
					packop_id = self.env['stock.pack.operation'].create(pack_datas)
					processed_ids.append(packop_id.id)
				#write quant
				quant = self.env['stock.quant'].search([
					('product_id','=',prod.product_id.id),
					('lot_id','=',prod.lot_id and prod.lot_id.id or False),
					('reservation_id','in',move_ids),
					('location_id','=',prod.sourceloc_id.id)])
				if not quant and prod.lot_id:
					quant = self.env['stock.quant'].search([
						('product_id','=',prod.product_id.id),
						('lot_id','=',prod.lot_id.id),
						('location_id','=',prod.sourceloc_id.id)])
				if quant:
					try:
						quant=quant[0]
					except:
						pass
					quant.sudo().write({
							'account_analytic_id': prod.account_analytic_id and prod.account_analytic_id.id or False,
							'account_analytic_dest_id': prod.account_analytic_dest_id and prod.account_analytic_dest_id.id or False,
							'employee_id': prod.employee_id and prod.employee_id.id or False,
							'is_loan': prod.is_loan,
						})

		# Delete the others
		packops = self.env['stock.pack.operation'].search(['&', ('picking_id', '=', self.picking_id.id), '!', ('id', 'in', processed_ids)])
		packops.unlink()

		# Execute the transfer of the picking
		self.picking_id.do_transfer()

		return True


class stock_transfer_details_items(models.TransientModel):
	_inherit = 'stock.transfer_details_items'

	employee_id = fields.Many2one('hr.employee', 'Employee', required=False)
	is_loan = fields.Boolean('Employee Loan')
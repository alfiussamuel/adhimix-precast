from odoo import api,fields,models,_ 
from odoo.exceptions import except_orm, Warning, RedirectWarning
import time

class AdhPreRealisasiProduksi(models.Model):
	_name = 'adhimix.pre.realisasi.produksi'

	name = fields.Char("No",readonly=True)
	company_id = fields.Many2one('res.company','Plant')
	nama_proyek_id = fields.Many2one('project.project','Nama Proyek')
	tanggal_realisasi = fields.Date("Tanggal Realisasi",default=lambda self:time.strftime("%Y-%m-%d"))
	partner_id = fields.Many2one('res.partner','Pelanggan',compute="_get_partner_id")
	cost_control_id = fields.Many2one('adhimix.pre.cost.control','No Cost Control')
	product_id = fields.Many2one('product.product','Nama Produk',compute="_get_product")
	sisa_rap = fields.Float("Sisa RAP",compute="_get_sisa_rap")
	volume_realisasi = fields.Float("Volume Realisasi")
	state = fields.Selection([('Draft','Draft'),('Approved','Approved')],'State',default='Draft')

	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('adhimix.pre.realisasi.produksi')
		return super(AdhPreRealisasiProduksi, self).create(vals)

	# @api.multi
	# def button_realisasi(self):
	# 	cost_control_obj = self.env['adhimix.pre.cost.control'].search([
	# 		('id','=',self.cost_control_id.id)
	# 		])
	# 	total = 0
	# 	for res in self.cost_control_id:
	# 		total = res.sisa_rap - self.volume_realisasi
	# 		cost_control_id = cost_control_obj.write({
	# 					'sisa_rap' : total,						
	# 			})
	@api.multi
	def button_approved(self):
		self.state = 'Approved'
		source_location = self.env['stock.location'].search([('name','=','Production')])
		dest_location = self.env['stock.warehouse'].search([('company_id','=',self.company_id.id)]).lot_stock_id

		for line in self:            
			move_vals = {
					'product_id': line.product_id.id,
					'product_uom_qty': line.volume_realisasi,
					'product_uom': line.product_id.uom_id.id,
					'name': line.product_id.name,
					'company_id': line.company_id.id,
					'date': line.tanggal_realisasi,
					'origin': line.name,
					'location_id': source_location.id,
					'location_dest_id':dest_location.id ,

					}            

			move = self.env['stock.move'].create(move_vals)
			move.action_confirm()
			move.action_assign()
			move.action_done()
			
		cost_control_obj = self.env['adhimix.pre.cost.control'].search([
				('id','=',self.cost_control_id.id)
				])
		total = 0
		for res in self.cost_control_id:
			total = res.sisa_rap - self.volume_realisasi
			cost_control_id = cost_control_obj.write({
						'sisa_rap' : total,						
				})
	# Domain Proyek Dan Cost Control
	@api.onchange('company_id','nama_proyek_id','cost_control_id')
	def onchange_company_id(self):
		ids_project = []
		ids_cost_control = []
		domain = {}
		project_lines = self.env['project.project'].search([
			('company_id','=',self.company_id.id)
			])
		cost_lines = self.env['adhimix.pre.cost.control'].search([
			('nama_proyek_id','=',self.nama_proyek_id.id)
			])
		for po_line in project_lines :
			ids_project.append(po_line.id)

		for cost_id in cost_lines :
			ids_cost_control.append(cost_id.id)

		domain = {'nama_proyek_id': [('id', '=', ids_project)],'cost_control_id' : [('id', '=', ids_cost_control)]} 
		return {'domain':domain}

	@api.one
	@api.depends('cost_control_id')
	def _get_product(self):
		for res in self.cost_control_id:
			self.product_id = res.product_id.id
	@api.one
	@api.depends('cost_control_id')
	def _get_partner_id(self):
		for res in self.cost_control_id:
			self.partner_id = res.pelanggan.id

	@api.one
	@api.depends('cost_control_id')
	def _get_sisa_rap(self):
		for res in self.cost_control_id:
			self.sisa_rap = res.sisa_rap

	# Warning Volume Realisasi
	@api.onchange('volume_realisasi')
	def onchange_volume_realisasi(self):
		if self.volume_realisasi :
			if self.volume_realisasi  > self.sisa_rap :
				value = {'volume_realisasi':0}
				warning = {
					'title': 'Warning',
					'message': 'Volume Realisasi Jangan Melebihi Sisa RAP !!!'
					}
				return {'value':value, 'warning':warning}

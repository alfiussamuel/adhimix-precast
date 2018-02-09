from odoo import api,fields,models,_ 
import time
from odoo.exceptions import except_orm, Warning, RedirectWarning

class AdhPrePermintanBarang(models.Model):
	_name = 'adhimix.pre.permintaan.barang'

	name = fields.Char("No",readonly=True)
	company_id = fields.Many2one('res.company','Plant')
	nama_proyek_id = fields.Many2one('project.project','Nama Proyek')
	tanggal_permintaan = fields.Date("Tanggal Permintaan",default=lambda self:time.strftime("%Y-%m-%d"))
	cost_control_id = fields.Many2one('adhimix.pre.cost.control','No Cost Control')
	product_line = fields.One2many('adhimix.pre.permintaan.barang.line','reference','Detail Produk')
	state = fields.Selection([('Draft','Draft'),('Approved','Approved')],'State',default="Draft")


	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('adhimix.pre.permintaan.barang')
		return super(AdhPrePermintanBarang, self).create(vals)

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

class AdhPrePermintanBarangLine(models.Model):
	_name = 'adhimix.pre.permintaan.barang.line'

	reference = fields.Many2one('adhimix.pre.permintaan.barang','reference')
	product_id = fields.Many2one('product.product','Produk')
	product_qty = fields.Float("Qty")

	@api.onchange('product_id')
	def onchange_product_id(self):
		ids_produk =[]
		for res in self.reference:
			cost_lines = self.env['adhimix.pre.cost.control.line'].search([
				('uraian_id','=',str(self.product_id.id)),('reference','=',res.cost_control_id.id)
				])
			print '=====================',cost_lines			
			# if not cost_lines:
			# 	raise Warning('Produk Harap Diisi !!!')
			for po_line in cost_lines :
				ids_produk.append(po_line.id)
				# print '=====================',ids_produk

			domain = {'product_id': [('id', 'in', ids_produk)]}
			return {'domain':domain}

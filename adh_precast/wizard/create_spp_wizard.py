from odoo import api,fields,models,_ 
import time
from odoo.exceptions import except_orm, Warning, RedirectWarning


class AdhPreCreateSppWizard(models.Model):
	_name ='adhimix.pre.create.spp.wizard'

	nama_proyek_id = fields.Many2one('project.project',"Nama Proyek")
	plant_id = fields.Many2one('res.company','Plant Utama')
	tanggal_kontrak = fields.Date("Tanggal Kontrak")
	plant_produksi_id = fields.Many2one('res.company','Plant Produksi')
	kontrak_id = fields.Many2one('sale.order','No Kontrak')
	kontrak_line_id = fields.Many2one('sale.order.line',"Sale Order Line")
	tanggal_pembuatan = fields.Date("Tanggal Pembuatan SPP",default=lambda self:time.strftime("%Y-%m-%d"))
	order_lines = fields.One2many('adhimix.pre.create.spp.wizard.line','reference','Detail Produk')
	# spp_line_ids = fields.One2many('adhimix.pre.daftar.spp','reference','Daftar SPP')

	@api.multi
	def create_buat_spp(self):
		# batas_produksi = 0
		
		for res in self.order_lines:
			if res.product_qty  > res.batas_produksi :
				raise Warning('Qty Tidak Boleh Melebihi Batas Produksi !!!')
			# Create SPP
			spp_id = self.env['adhimix.pre.spp'].create({															
														'kontrak_id': self.kontrak_id.id,
														'nama_proyek_id' : self.nama_proyek_id.id,
														'tanggal': self.tanggal_pembuatan,
														'plant_id' : self.plant_produksi_id.id																								
														})
			
			
				# Create SPP Line
			spp_product_id = self.env['adhimix.pre.spp.line'].create({																		
																	'reference' : spp_id.id,
																	'name' : res.product_id.name, 
																	'product_id' : res.product_id.id,
																	'satuan_barang' : res.product_id.uom_id.id,
																	'qty' : res.product_qty,
																	})
			sale_line_obj = self.env['sale.order.line'].search([('order_id','=',self.kontrak_id.id),
																('product_id','=',res.product_id.id)])
			sale_line_id = sale_line_obj.write({
												'batas_produksi': res.batas_produksi - res.product_qty
												})
			for res in self.kontrak_id:
				for line in res.order_line:
					spp_line_id = self.env['adhimix.pre.daftar.spp.line'].create({
																			'reference' : line.id,
																			'spp_id'	: spp_id.id,
																			'plant_id'	: self.plant_produksi_id.id,
																			'tanggal_pembuatan' : self.tanggal_pembuatan
																			})

					print '=========================='
					print 'MUNCULKAN SPP',spp_line_id
					print '=========================='					
		

class AdhPreCreateSppWizard(models.Model):
	_name = 'adhimix.pre.create.spp.wizard.line'

	reference = fields.Many2one('adhimix.pre.create.spp.wizard','reference')
	product_id = fields.Many2one('product.product','Nama Barang')
	satuan_barang = fields.Many2one('product.uom','Satuan Barang')
	product_qty = fields.Float('Qty',default=0.00)
	batas_produksi = fields.Float("Batas Produksi",readonly=True)

# class AdhPreDaftarSpp(models.Model):
# 	_name = 'adhimix.pre.daftar.spp'

# 	reference = fields.Many2one('adhimix.pre.create.spp.wizard','reference')
# 	spp_id = fields.Many2one('adhimix.pre.spp','Nomor SPP')
# 	plant_id = fields.Many2one('res.company','Plant')
# 	tanggal_pembuatan = fields.Date(string="Tanggal Pembuatan")


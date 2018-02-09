from odoo import api,fields,models,_ 


class AdhimixCreatePermintaanEstimasi(models.Model):
	_name = 'adhimix.create.permintaan.estimasi'


	tanggal_permintaan = fields.Date("Tanggal Permintaan",readonly=True)
	product_id = fields.Many2one('product.product',"Produk",readonly=True)
	category_id = fields.Many2one('product.category',"Kategori Produk",readonly=True)
	bom_id = fields.Many2one('mrp.bom',"BOM Standar",readonly=True)
	info_pasar_product_id = fields.Many2one('adhimix.pre.info.pasar.product','Estimasi')
	info_pasar_product_estimasi_id = fields.Many2one('adhimix.pre.info.pasar.product.estimasi','Estimasi')
	produk_baru = fields.Char("Produk Baru",readonly=True)
	tanggal_butuh = fields.Date("Tanggal Butuh")
	pelanggan_id = fields.Many2one('res.partner','Pelanggan')
	nama_proyek = fields.Char("Nama Proyek",readonly=True)
	keterangan = fields.Text("Keterangan")
	hpp_loko_pabrik = fields.Boolean("HPP Loko Pabrik")
	hpp_terkirim = fields.Boolean("HPP Terkirim")
	hpp_stressing = fields.Boolean("HPP Stressing")
	hpp_terinstall = fields.Boolean("HPP Terinstall")
	desain = fields.Boolean("Desain")
	metode_kerja = fields.Boolean("Metode Kerja")
	shop_drawing = fields.Boolean("Shop Drawing")


	@api.multi
	def create_permintaan_estimasi(self):
		permintaan_obj = self.env['adhimix.pre.permintaan.estimasi']
		vals = permintaan_obj.create({
				'product_id'		: self.product_id.id,
				'info_pasar_product_id':self.info_pasar_product_id.id,
				'info_pasar_product_estimasi_id' : self.info_pasar_product_estimasi_id.id,
				'produk_baru'		: self.produk_baru,
				'tanggal_permintaan': self.tanggal_permintaan,
				'tanggal_butuh'		: self.tanggal_butuh,
				'pelanggan_id'		: self.pelanggan_id.id,
				'nama_proyek'		: self.nama_proyek,
				'hpp_loko_pabrik'   : self.hpp_loko_pabrik,
				'hpp_terkirim'		: self.hpp_terkirim,
				'hpp_stressing'		: self.hpp_stressing,
				'hpp_terinstall'	: self.hpp_terinstall,
				'desain'			: self.desain,
				'metode_kerja'		: self.metode_kerja,
				'shop_drawing'		: self.shop_drawing,
				'keterangan'		: self.keterangan,
				'category_id'		: self.category_id.id
				
		})
		self.env['adhimix.pre.info.pasar.product.estimasi'].create({
								'estimasi_id':vals.id,
								'reference' : self.info_pasar_product_id.id,})
		# self.info_pasar_product_estimasi_id.write({'estimasi_id' : vals.id})
		# self.estimasi_id = vals.id	
		return {
				  'name': ('Permintaan Estimasi'),
				  'view_type': 'form',
				  'view_mode': 'form',
				  'res_model': 'adhimix.pre.permintaan.estimasi',
				  'res_id': vals.id,
				  'type': 'ir.actions.act_window',
		}
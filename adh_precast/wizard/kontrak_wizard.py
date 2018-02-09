from odoo import api,fields,models,_ 
import time

class AdhMrpKontrakWizard(models.Model):
	_name = "adhimix.mrp.kontrak.wizard"

	name = fields.Char("No Kontrak")
	sale_id = fields.Many2one(comodel_name="sale.order",string="Nomor Penawaran")
	tanggal = fields.Date("Tanggal")
	pekerjaan = fields.Text("Pekerjaan")
	lokasi = fields.Text("Lokasi")
	spesifikasi = fields.Text("Spesifikasi")
	waktu_pelaksanaan = fields.Date("Mulai Pelaksanaan")
	waktu_pelaksanaan_end = fields.Date("Selesai Pelaksanaan")
	harga_negosiasi = fields.Float("Harga Negosiasi")
	# cara_pembayaran = fields.Text("Cara Pembayaran")
	cara_pembayaran_id = fields.Many2one('adhimix.cara.Pembayaran',"Cara Pembayaran")
	scope_pekerjaan_owner = fields.Text("Scope Pekerjaan PT. API")
	scope_pekerjaan_client = fields.Text("Scope Pekerjaan Pelanggan")
	nama_pelanggan = fields.Many2one(comodel_name="res.partner",string="Nama Pelanggan")
	lampiran = fields.Many2many(comodel_name="ir.attachment",string="Lampiran")
	company_id = fields.Many2one(comodel_name="res.company",string="Company",default=lambda self:self.env.user,readonly=True)
	
	
	@api.multi
	def create_berita_acara(self):
		kontrak_obj = self.env['adhimix.mrp.kontrak']
		kontrak_product_obj = self.env['adhimix.mrp.kontrak.product']
		kontrak_bom_obj = self.env['adhimix.mrp.kontrak.product.bom']

		kontrak_id = kontrak_obj.create({
			# 'name'		: self.id,
			'sale_id'	: self.sale_id.id,
			'tanggal'	: self.tanggal,
			'pekerjaan'	: self.pekerjaan,
			'lokasi'	: self.lokasi,
			'spesifikasi': self.spesifikasi,
			'waktu_pelaksanaan': self.waktu_pelaksanaan,
			'waktu_pelaksanaan_end': self.waktu_pelaksanaan_end,
			'harga_negosiasi'	: self.harga_negosiasi,
			# 'cara_pembayaran'	: self.cara_pembayaran,
			'cara_pembayaran_id'	: self.cara_pembayaran_id.id,
			'scope_pekerjaan_owner':self.scope_pekerjaan_owner,
			'scope_pekerjaan_client': self.scope_pekerjaan_client,
			'nama_pelanggan'	: self.nama_pelanggan.id,
			'lampiran'	: self.lampiran,
			'company_id' : self.company_id.id,
			})
		for res in self.sale_id.order_line:
			kontrak_line = kontrak_product_obj.create({
				'product_id'	: res.product_id.id,
				'satuan_barang' : res.product_uom.id,
				'qty'			: res.product_uom_qty,
				'price_unit'	: res.price_unit,
				'reference'		: kontrak_id.id
					})
			# for data in self.sale_id.order_line:
			for line in res.bom_list:
				kontrak_bom_id = kontrak_bom_obj.create({
					'product_id'	: line.product_id.id,
					'satuan_barang' : line.product_id.uom_id.id,
					'qty'			: line.qty,
					'price_unit'	: line.product_id.standard_price,
					'reference'		: kontrak_line.id,
					})

		return {
				  'name': ('BA &#38; Negosiasi '),
				  'view_type': 'form',
				  'view_mode': 'form',
				  'res_model': 'adhimix.mrp.kontrak',
				  'res_id': kontrak_id.id,
				  'type': 'ir.actions.act_window',
				}
			


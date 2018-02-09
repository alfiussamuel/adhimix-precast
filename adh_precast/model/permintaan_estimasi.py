from odoo import api,fields,models,_ 
# from datetime import timedelta
from datetime import datetime, timedelta
import time
# from dateutil.relativedelta import relativedelta 
from odoo.exceptions import except_orm, Warning, RedirectWarning

class AdhimixPrePermintaanEstimasi(models.Model):
	_name = 'adhimix.pre.permintaan.estimasi'

	name = fields.Char("Nomor Permintaan",readonly=True)
	product_id = fields.Many2one('product.product','Produk')
	category_id = fields.Many2one('product.category',"Kategori Produk",readonly=True)
	bom_id = fields.Many2one('mrp.bom','Bill of Material')
	produk_baru = fields.Char("Produk Baru")
	info_pasar_product_id = fields.Many2one('adhimix.pre.info.pasar.product','Estimasi')
	info_pasar_product_estimasi_id = fields.Many2one('adhimix.pre.info.pasar.product.estimasi','Estimasi Detail')
	# is_tanggal_butuh = fields.Boolean(compute="_get_tanggal_butuh")
	tanggal_permintaan = fields.Date("Tanggal Permintaan",default=lambda self:time.strftime("%Y-%m-%d"))
	tanggal_butuh = fields.Date("Tanggal Butuh")
	pelanggan_id = fields.Many2one('res.partner','Pelanggan')
	nama_proyek = fields.Char("Nama Proyek")
	keterangan = fields.Text("Keterangan")
	state = fields.Selection([('Draft','Draft'),('Sah','Sah')],string='Status',default='Draft')
	hpp_loko_pabrik = fields.Boolean("HPP Loko Pabrik")
	hpp_terkirim = fields.Boolean("HPP Terkirim")
	hpp_stressing = fields.Boolean("HPP Stressing")
	hpp_terinstall = fields.Boolean("HPP Terinstall")
	desain = fields.Boolean("Desain")
	metode_kerja = fields.Boolean("Metode Kerja")
	shop_drawing = fields.Boolean("Shop Drawing")
	# tanggal = fields.Date('Tanggal Produksi',default=lambda *a:(datetime.today()+relativedelta(days=3)).strftime('%Y-%m-%d'), )
	# bom_list_ids = fields.One2many('')


	# @api.one
	# @api.depends('tanggal_butuh')
	# def _get_tanggal_butuh(self):
	# 	df = datetime.strptime(self.tanggal_butuh,'%Y-%m-%d') + timedelta(days=3)
	# 	# df = datetime.strptime(self.tanggal_permintaan,'%Y-%m-%d')
	# 	# delta = timedelta(days=3)
	# 	for res in self:
	# 		if df<= fields.Date.today() :
	# 			res.is_tanggal_butuh = True
	# 			# fields.Date.today() = delta
	# 			# print 'AAAAAAAAAa',res.is_tanggal_butuh

	@api.onchange('bom_id')
	def onchange_bom_id(self):
		for res in self.bom_id:
			self.product_id = res.product_tmpl_id.id
	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('adhimix.pre.permintaan.estimasi')			
		return super(AdhimixPrePermintaanEstimasi, self).create(vals)

	@api.multi
	def action_sah(self):
		self.state = 'Sah'
		# if not self.produk_baru:
		# 	raise Warning('Produk Belum Terdaftar & BOM Tidak Ada !!!')
		if not self.bom_id :
			raise Warning('BOM Standar Tidak Ada,Harap Isi Dahulu !!!')
		elif not self.product_id:
			raise Warning('BOM Standar Tidak Ada,Harap Isi Dahulu !!!')
		else:
			self.info_pasar_product_id.write({
				'product_id' : self.product_id.id,
				'bom_id'	: self.bom_id.id,
				'satuan_id'	: self.product_id.uom_id.id
				})
			# self.info_pasar_product_estimasi_id.write({
			# 	'estimasi_id'		: self.id,
			# 	'status_estimasi' : self.state
			# 	})
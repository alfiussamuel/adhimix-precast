from odoo import api, fields, models, _
import time
from datetime import datetime, date
from odoo.exceptions import except_orm, Warning, RedirectWarning
from . import info_pasar_stage

class AdhimixPreInfoPasar(models.Model):
	_name = "adhimix.pre.info.pasar"

	name = fields.Char(string="No",readonly=True)
	tanggal_rencana_kontrak = fields.Date(string="Tanggal Rencana Kontrak")
	persentase_keyakinan = fields.Selection([('<50%','<50%'),('50-60%','50-60%'),('60-70%','60-70%'),('70-80%','70-80%'),('80-90%','80-90%'),('90-100%','90-100%')],string="Persentase Keyakinan")
	tanggal_informasi = fields.Date(string="Tanggal Informasi Pasar",required=True,default=lambda self:time.strftime("%Y-%m-%d"))
	kanban_state = fields.Selection([('grey', 'No next activity planned'), ('red', 'Next activity late'), ('green', 'Next activity is planned')],
        			string='Activity State', compute='_compute_kanban_state')
	company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
	color = fields.Integer('Color Index', default=0)
	active = fields.Boolean('Active', default=True)
	priority = fields.Selection(info_pasar_stage.AVAILABLE_PRIORITIES, string='Rating', index=True, default=info_pasar_stage.AVAILABLE_PRIORITIES[0][0])
	nama_proyek = fields.Char("Nama Proyek")
	lokasi = fields.Char(string="Lokasi")
	pic = fields.Many2one('res.users',"PIC")
	created_by = fields.Many2one('res.users',default=lambda self:self.env.user,readonly=True,string="Dibuat Oleh")
	nilai_proyek = fields.Float("Nilai Proyek")
	tanggal_efektif = fields.Date(string="Tanggal Efektif",default=lambda self:time.strftime("%Y-%m-%d"))
	sumber_informasi_dari = fields.Selection([('OWNER','OWNER'),('REKANAN','REKANAN'),
											('KONSULTAN','KONSULTAN'),('KONTRAKTOR','KONTRAKTOR')],string="Dari")
	sumber_informasi_cara = fields.Many2one('adhimix.cara.sumber.informasi',string="Cara")
	nama = fields.Char(string="Nama")
	telepon = fields.Char(string="Telepon")
	status = fields.Selection([('Klarifikasi/Negosiasi','Klarifikasi/Negosiasi'),('Kontrak','Kontrak'),('Lain-Lain','Lain-Lain'),
								('Pelaksanaan','Pelaksanaan'),('Penawaran','Penawaran'),('Penetapan Pemenang','Penetapan Pemenang'),
								('Pra Kualifikasi (PQ)','Pra Kualifikasi (PQ)'),('Tender','Tender')],string="Status",default="Klarifikasi/Negosiasi") 
	ya = fields.Boolean(string="Ya")
	tidak = fields.Boolean(string="Tidak")
	tanggal = fields.Date(string="Tanggal")
	company_id = fields.Many2one(comodel_name="res.company",string="Organisasi",default=lambda self:self.env.user,readonly=True)
	state = fields.Selection([('Info Pasar','Info Pasar'),('Analisa Pasar','Analisa Pasar'),('Target Pasar','Target Pasar')],string="Status",default="Info Pasar",required=True)
	jenis_proyek_id = fields.Many2one('adhimix.jenis.proyek','Jenis Proyek')

	kota_id = fields.Many2one('vit.kota','Kota',domain="[('state_id', '=', provinsi_id)]")
	provinsi_id = fields.Many2one('res.country.state','Provinsi')

	sumber_dana = fields.Selection([('APBD','APBD'),('APBN','APBN'),
													('Pinjaman Luar Negeri','Pinjaman Luar Negeri'),('Lain-Lain','Lain-Lain')],
													string="Sumber Dana")
	# owner
	is_owner = fields.Boolean("Owner Baru")
	owner_id = fields.Many2one('res.partner',"Owner")
	nama_owner = fields.Char("Owner Belum Register")
	
	# Waktu Pelaksanaan 
	mulai = fields.Date("Mulai")
	selesai = fields.Date("Selesai")
	
	# Konsultan
	is_konsultan =  fields.Boolean("Konsultan Baru")
	konsultan_id = fields.Many2one('res.partner','Konsultan')
	nama_konsultan = fields.Char("Konsultan Belum Register")	
	product_detail_ids = fields.One2many('adhimix.pre.info.pasar.product','reference','Produk Detail')
	kontraktor_ids = fields.One2many('adhimix.pre.info.pasar.kontraktor','reference','Kontraktor')
	grand_total = fields.Integer("Total",compute="_grand_total")
	
	#Analisa Pasar
	kep_owner = fields.Selection([('Ya','Ya'),('Tidak','Tidak')],'Owner')
	ket_owner = fields.Text("Keterangan")
	kep_status_bayar = fields.Selection([('Ya','Ya'),('Tidak','Tidak')],'Status Bayar')
	ket_status_bayar = fields.Text("Keterangan")
	kep_sumber_dana = fields.Selection([('Ya','Ya'),('Tidak','Tidak')],'Sumber Dana')
	ket_sumber_dana = fields.Text("Keterangan")
	modal_kerja = fields.Char("Modal Kerja")
	kep_modal_kerja = fields.Selection([('Ya','Ya'),('Tidak','Tidak')])
	ket_modal_kerja = fields.Text("Keterangan")
	pelaksanaaan_mulai = fields.Date("Mulai")
	pelaksanaaan_selesai = fields.Date("Selesai")
	kep_mulai = fields.Selection([('Ya','Ya'),('Tidak','Tidak')])
	ket_mulai = fields.Text("keterangan")
	kategori_proyek = fields.Selection([('Multi Tahun','Multi Tahun'),('Tahun Tunggal','Tahun Tunggal')],'Kategori Proyek')
	kep_kategori_proyek = fields.Selection([('Ya','Ya'),('Tidak','Tidak')])
	ket_kategori_proyek = fields.Text("Keterangan")
	spesifikasi_khusus = fields.Char("Spesifikasi Khusus")
	kep_spesifikasi_khusus = fields.Selection([('Ya','Ya'),('Tidak','Tidak')])
	ket_spesifikasi_khusus = fields.Text("Keterangan")
	kep_kapasitas_produksi = fields.Selection([('Ya','Ya'),('Tidak','Tidak')],'Kapasitas Produksi')
	ket_kapasitas_produksi = fields.Text("Keterangan")
	keputusan_akhir = fields.Selection([('Ya','Ya'),('Tidak','Tidak'),('Disposisi','Disposisi')],'Keputusan Akhir')

	@api.multi
	def _compute_kanban_state(self):
		today = date.today()
		for lead in self:
			kanban_state = 'grey'
		if lead.tanggal_informasi:
			lead_date = fields.Date.from_string(lead.tanggal_informasi)
		if lead_date >= today:
			kanban_state = 'green'
		else:
			kanban_state = 'red'
		lead.kanban_state = kanban_state


	@api.depends('product_detail_ids')
	def _grand_total(self):
		for rec in self:
			if rec.product_detail_ids:
				for x in rec.product_detail_ids:
					rec.grand_total += x.estimasi_biaya

	@api.multi
	def action_target_pasar(self, vals, default=None):
		self.state = 'Target Pasar'

	def action_analisa_pasar(self):
		if self.is_owner:
			if not self.nama_owner:
				raise Warning('Kolom Owner harus diisi untuk Analisa !!!')
		elif not self.is_owner:
			if not self.owner_id:
				raise Warning('Kolom Owner harus diisi untuk Analisa !!!')
		if not self.sumber_dana:			
			raise Warning('Kolom Sumber Dana harus diisi untuk Analisa !!!')
		self.state = 'Analisa Pasar'

	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('adhimix.pre.info.pasar')			
		return super(AdhimixPreInfoPasar, self).create(vals)



class AdhimixPreInfoPasarKontraktor(models.Model):
	_name 	= 'adhimix.pre.info.pasar.kontraktor'

	reference = fields.Many2one('adhimix.pre.info.pasar')		
	is_kontraktor = fields.Boolean("Kontraktor Baru")
	kontraktor_id = fields.Many2one('res.partner',"Kontraktor")
	nama_kontraktor = fields.Char("Kontraktor Belum Register")
	

	@api.multi
	def button_buat_penawaran(self):
		penawaran_obj = self.env['sale.order']
		penawaran_detail_obj = self.env['sale.order.line']
		penawaran_detail_bom_obj = self.env['sale.order.line.bom']
		penawaran_detail_bom_pengiriman_obj = self.env['sale.order.line.bom.pengiriman']
		penawaran_detail_bom_stressing_obj = self.env['sale.order.line.bom.stressing']
		penawaran_detail_bom_install_obj = self.env['sale.order.line.bom.install']
		sale_order_id = penawaran_obj.create({ 
			'partner_id'	: self.kontraktor_id.id,
			'date_order' 	: fields.Date.today(),
			'nama_proyek'	: self.reference.nama_proyek,
			'company_id'	: self.reference.company_id.id,
			'info_pasar_id' : self.reference.id
			})
		
		for data in self.reference.product_detail_ids:
			sale_order_line_id =  penawaran_detail_obj.create({
				'jenis_produk'	  : data.product_id.jenis_produk,
				'product_id'	  : data.product_id.id,
				'name'			  : data.product_id.name,
				'product_uom'	  : data.product_id.uom_id.id,
				'order_id'	 	  : sale_order_id.id,
				'bom_id'		  : data.bom_id.id,
				'product_uom_qty' : data.vol_market_share,
				'price_unit'	  : data.harga_satuan,
				'customer_lead'	  : 1,
			})
			# if data.bom_id:
			for bom_line in data.bom_id.bom_line_ids:							
				penawaran_detail_bom_obj.create({
					'product_id'	: bom_line.product_id.id,
					'satuan_barang' : bom_line.product_id.uom_id.id,
					'price_unit'	: bom_line.product_id.standard_price,
					'price_subtotal' : bom_line.product_qty * bom_line.product_id.standard_price,
					'qty'			: bom_line.product_qty,
					'reference'		: sale_order_line_id.id
					})				
			
			for pengiriman in data.bom_id.pengiriman_ids:
				penawaran_detail_bom_pengiriman_obj.create({
					'product_id'	 : pengiriman.product_id.id,				
					'product_qty'	 : pengiriman.product_qty,
					'koefisien'		 : pengiriman.koefisien,
					'price_unit'	 : pengiriman.product_id.standard_price,							
					'reference'		 : sale_order_line_id.id
					})
			
			for stressing in data.bom_id.stressing_ids:
				penawaran_detail_bom_stressing_obj.create({
					'product_id'	 : stressing.product_id.id,				
					'product_qty'	 : stressing.product_qty,
					'koefisien'		 : stressing.koefisien,
					'price_unit'	 : stressing.product_id.standard_price,							
					'reference'		 : sale_order_line_id.id
					})
		
			for install in data.bom_id.install_ids:
				penawaran_detail_bom_install_obj.create({
					'product_id'	 : install.product_id.id,				
					'product_qty'	 : install.product_qty,
					'koefisien'		 : install.koefisien,
					'price_unit'	 : install.product_id.standard_price,							
					'reference'		 : sale_order_line_id.id
					})
				
		return {
				  'name': ('Penawaran'),
				  'view_type': 'form',
				  'view_mode': 'form',
				  'res_model': 'sale.order',
				  'res_id': sale_order_id.id,
				  'type': 'ir.actions.act_window',
		}
	
class AdhimixPreInfoPasar_product(models.Model):
	_name 	= 'adhimix.pre.info.pasar.product'

	reference = fields.Many2one('adhimix.pre.info.pasar')
	# kelompok_id = fields.Many2one('adhimix.product.level',"Kelompok Produk")
	is_product = fields.Boolean("Produk Baru ?")
	product_id = fields.Many2one('product.product','Produk')
	category_id = fields.Many2one('product.category','Kategori Produk')
	produk_baru = fields.Char("Produk Baru")
	# type_id = fields.Many2one('adhimix.product.type',"Jenis Produk")
	bom_id = fields.Many2one('mrp.bom','BOM Standar')
	satuan_id = fields.Many2one('product.uom','Satuan')
	estimasi_biaya = fields.Integer("Estimasi Biaya",compute="_get_biaya_estimasi")
	harga_satuan = fields.Float("Harga Satuan")
	vol_market_size = fields.Float("Volume Market Size")
	total_market_size = fields.Float("Total Market Size",compute="_get_total_market_size")
	vol_market_share = fields.Float("Volume Market Share")
	total_market_share = fields.Float("Total Market Share",compute="_get_total_market_share")
	estimasi_ids = fields.One2many('adhimix.pre.info.pasar.product.estimasi','reference','Permintaan Estimasi')
	# estimasi_id = fields.Many2one('adhimix.pre.permintaan.estimasi','Estimasi')
	# status_estimasi = fields.Char("Status Estimasi",compute="_get_status_estimasi")

	
	# @api.depends('estimasi_id')
	# def _get_status_estimasi(self):
	# 	for line in self:
	# 		line.status_estimasi = line.estimasi_id.state
		
	@api.onchange('product_id')
	def onchange_product_id(self):
		self.satuan_id = self.product_id.uom_id
		self.harga_satuan = self.product_id.list_price
		if self.product_id.bom_ids:
			self.bom_id = self.product_id.bom_ids[0]

	# Domain Filter
	@api.onchange('product_id')
	def onchange_product_id(self):
		ids_product = []
		domain = {}
		product_lines = self.env['mrp.bom'].search([
			('product_tmpl_id.id','=',self.product_id.product_tmpl_id.id)
		])
		for po_line in product_lines :
			ids_product.append(po_line.id)
			
		domain = {'bom_id': [
					('id', 'in', ids_product),
					# ('plant_id', '=', self.order_id.plant_utama.id)
		]} 
		return {'domain':domain}

	
	@api.depends('vol_market_share','bom_id.bom_line_ids')
	def _get_biaya_estimasi(self):
		for rec in self:
			subtotal = 0
			for line in rec.bom_id:
				for res in line.bom_line_ids:
				# line.subtotal += (line.product_qty * line.price_unit)
					subtotal += res.subtotal 
					price = rec.vol_market_share * subtotal
					rec.estimasi_biaya = price


	@api.depends('harga_satuan','vol_market_size')
	def _get_total_market_size(self):
		for line in self:
			price = line.harga_satuan * line.vol_market_size
			line.total_market_size = price

	@api.depends('harga_satuan','vol_market_share')
	def _get_total_market_share(self):
		for line in self:
			price = line.harga_satuan * line.vol_market_share
			line.total_market_share = price

	@api.multi
	def button_estimasi(self, vals):
		ir_model_data = self.env['ir.model.data']
		compose_form_id = ir_model_data.get_object_reference('adh_precast', 'create_permintaaan_estimasi_wizard')[1]
		order_line = []
		# # for data in self:
		# if not self.bom_id :
		# 	raise Warning('BOM Standar Tidak Ada,Harap Isi Dahulu !!!')
		# elif not self.product_id:
		# 	raise Warning('Produk Tidak Ada,Harap Isi Dahulu !!!')
		# else:
		order_line.append({
		'tanggal_permintaan' 		: fields.Date.today(),		
		'nama_proyek'				: self.reference.nama_proyek,
		'product_id'  				: self.product_id.id,
		'bom_id'  					: self.bom_id.id,
		'produk_baru'				: self.produk_baru,
		'info_pasar_product_id'		: self.id,
		})
		return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'adhimix.create.permintaan.estimasi',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': {
	                'default_tanggal_permintaan': fields.Date.today (),
	                'default_nama_proyek': self.reference.nama_proyek,
	                'default_product_id': self.product_id.id,
	                'default_bom_id': self.bom_id.id,
	                'default_produk_baru': self.produk_baru,
	                'default_info_pasar_product_id': self.id,
	                'default_category_id' : self.category_id.id
	            }
            }

class AdhimixPreInfoPasarProductEstimasi(models.Model):
	_name = 'adhimix.pre.info.pasar.product.estimasi'

	reference = fields.Many2one('adhimix.pre.info.product.estimasi')
	estimasi_id = fields.Many2one('adhimix.pre.permintaan.estimasi','Estimasi')
	status_estimasi = fields.Char("Status Estimasi",compute="_get_status_estimasi")


	@api.depends('estimasi_id')
	def _get_status_estimasi(self):
		for line in self:
			line.status_estimasi = line.estimasi_id.state

# Tabel Jenis proyek
class AdhimixJenisProyek(models.Model):
	_name = 'adhimix.jenis.proyek'

	name = fields.Char("Name")
	description = fields.Char("Description")
	

class AdhCaraSumberInformasi(models.Model):
	_name = 'adhimix.cara.sumber.informasi'

	name = fields.Char("Nama")
	description = fields.Char("Description")


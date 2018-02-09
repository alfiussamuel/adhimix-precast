from odoo import api,fields,models,_
import datetime
import time
import calendar
from odoo.tools import amount_to_text_en
from odoo.exceptions import except_orm, Warning, RedirectWarning


class SaleOrderCost(models.Model):
	_name = "sale.order.cost"
		
	reference = fields.Many2one(comodel_name="sale.order",string="Reference")	
	nama_biaya = fields.Many2one(comodel_name="adhimix.biaya",string="Nama Biaya")
	jenis_biaya = fields.Selection([('Persentase','Persentase'),('Nominal','Nominal')],"Jenis Biaya")
	nilai_biaya = fields.Float(string="Nilai Biaya")
	total_biaya = fields.Float("Total Biaya",compute="_get_total_biaya")			
	
	@api.depends('nilai_biaya','jenis_biaya','reference.order_line')
	def _get_total_biaya(self):
		for rec in self :
			if rec.jenis_biaya == 'Persentase' :
				total = rec.nilai_biaya * rec.reference.amount_untaxed / 100
				rec.total_biaya = total
			else :
				rec.total_biaya = rec.nilai_biaya
				
class AdhimixBiaya(models.Model):
	_name = "adhimix.biaya"
			
	name = fields.Char(string="Nama Biaya")
	account_id = fields.Many2one("account.account", string="Account")			

class AdhimixTemplateBiaya(models.Model):
	_name = "adhimix.template.biaya"
			
	name = fields.Char("Template Biaya")
	list_biaya = fields.One2many(comodel_name="adhimix.template.biaya.line",inverse_name="reference",string="Biaya Lain")		
	
class AdhimixTemplateBiayaLine(models.Model):
	_name = "adhimix.template.biaya.line"
				
	reference = fields.Many2one("adhimix.template.biaya", string="Nama Biaya")
	biaya_id = fields.Many2one("adhimix.biaya", string="Nama Biaya")
	jenis_biaya = fields.Selection([('Persentase','Persentase'),('Nominal','Nominal')],"Jenis Biaya")
	nilai_biaya = fields.Float(string="Nilai Biaya")
	
class SaleOrder(models.Model):
	_inherit = "sale.order"

	@api.depends('amount_total')
	def _terbilang(self):
		for rec in self:
			amount = rec.amount_total
			terbilang = self.env['wit.terbilang'].terbilang(amount,'IDR')
			rec.terbilang = terbilang


	terbilang = fields.Char(string="Terbilang", required=False, compute="_terbilang")
	kondisi_penawaran_ids = fields.One2many(comodel_name="sale.order.line",inverse_name="reference",string="Kondisi Penawaran")

	perihal = fields.Text("Perihal")
	nama_proyek = fields.Char("Nama Proyek")
	nama_proyek_id = fields.Many2one(comodel_name='project.project',string='Nama Proyek')
	company_id = fields.Many2one(comodel_name="res.company",string="Company")
	negosiasi_line_ids = fields.One2many(comodel_name='sale.order',inverse_name='penawaran_id',string='Negosiasi Line')
	is_negosiasi = fields.Boolean("Is Negosiasi",readonly=True)
	pic = fields.Char("PIC")
	info_pasar_id = fields.Many2one('adhimix.pre.info.pasar','Nomor Info Pasar')
	# sale_id = fields.Many2one('sale.order')	
	kontrak_id = fields.Many2one("adhimix.mrp.kontrak", string="No. Kontrak")
	spp_id = fields.Many2one("adhimix.pre.spp", string="No. SPP")
	list_biaya = fields.One2many(comodel_name="sale.order.cost",inverse_name="reference",string="Biaya Lain")
	template_biaya_id = fields.Many2one("adhimix.template.biaya", string="Template Biaya")
	status_negosiasi = fields.Char("Status Negosiasi",compute="_get_status_negosiasi")	
	total_hpp = fields.Float("HPP",compute="_get_total_hpp_all")
	total_biaya_langsung = fields.Float("Pembebanan",compute="_get_total_biaya_langsung")
	grand_total_biaya = fields.Float("Total Biaya",compute="_get_total_biaya")
	total_penjualan = fields.Float("Total Penjualan",compute="_get_total_penjualan")
	total_profit = fields.Float("Profit",compute="_get_total_profit")
	nomor_penawaran = fields.Char("Nomor Penawaran",readonly=True,)
	nomor_negosiasi 	= fields.Char("Nomor Negosiasi",readonly=True,)
	penawaran_id = fields.Many2one('sale.order', 'Nomor Penawaran', readonly=True)
	persentase_negosiasi = fields.Float("Negosiasi",compute="_get_button_persentase")
	state = fields.Selection([
        ('draft', 'Penawaran'),
        ('sent', 'Negosiasi'),
        # ('berita acara', 'Berita Acara'),
        ('sale', 'SO/Kontrak'),
        # ('Kontrak','Kontrak'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')], 'Status',default='draft')


	def name_get(self):
		res = []
		for rec in self:
			if rec.state == 'draft':
				name = rec.nomor_penawaran
				#res.append((rec.id, name + "-" + rec.code ))
				res.append((rec.id, name ))
			elif rec.state == 'sent':
				name = rec.nomor_negosiasi
				#res.append((rec.id, name + "-" + rec.code ))
				res.append((rec.id, name ))
			elif rec.state == 'sale':
				name = rec.name
				res.append((rec.id, name ))
			elif rec.state == 'done':
				name = rec.name
				res.append((rec.id, name ))
			elif rec.state == 'cancel':
				name = rec.name
				res.append((rec.id, name ))
			else:
				res.append((rec.id, rec.state))
		return res
 	
	@api.model
	def create(self, vals):
		if vals.get('name', _('New')) == _('New'):
			if 'company_id' in vals:
				vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('sale.order') or _('New')
				vals['nomor_penawaran'] = self.get_sequence('Kode Nomor Penawaran','sale.order.custom.penawaran','PNW/'%vals)
				vals['nomor_negosiasi'] = self.get_sequence('Kode Nomor Negosiasi','sale.order.custom.negosiasi','NEGO/'%vals)
			else:
				vals['name'] = self.env['ir.sequence'].next_by_code('sale.order') or _('New')
				vals['nomor_penawaran'] = self.get_sequence('Kode Nomor Penawaran','sale.order.custom.penawaran','PNW/'%vals)
				vals['nomor_negosiasi'] = self.get_sequence('Kode Nomor Negosiasi','sale.order.custom.negosiasi','NEGO/'%vals)

		# Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
		if any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id']):
			partner = self.env['res.partner'].browse(vals.get('partner_id'))
			addr = partner.address_get(['delivery', 'invoice'])
			vals['partner_invoice_id'] = vals.setdefault('partner_invoice_id', addr['invoice'])
			vals['partner_shipping_id'] = vals.setdefault('partner_shipping_id', addr['delivery'])
			vals['pricelist_id'] = vals.setdefault('pricelist_id', partner.property_product_pricelist and partner.property_product_pricelist.id)
		result = super(SaleOrder, self).create(vals)
		return result



	def get_sequence(self, name=False, obj=False, pref=False, context=None):
		sequence_id = self.env['ir.sequence'].search([
			('name', '=', name),
			('code', '=', obj),
			('prefix', '=', pref + '%(month)s-%(year)s/')
		])
		if not sequence_id :
			sequence_id = self.env['ir.sequence'].sudo().create({
				'name': name,
				'code': obj,
				'implementation': 'no_gap',
				'prefix': pref + '%(month)s-%(year)s/',
				'padding': 3
			})
		return sequence_id.next_by_id()

	@api.onchange('template_biaya_id')
	def onchange_template_biaya(self):
		biaya_list = []
		if self.template_biaya_id :
			for rec in self.template_biaya_id.list_biaya:
				biaya_list.append({
                            'nama_biaya' : rec.biaya_id.id,
                            'jenis_biaya' : rec.jenis_biaya,
                            'nilai_biaya' : rec.nilai_biaya,
                            })
			return {'value': {
                    'list_biaya': biaya_list, 
                    }}
	# Total Negosiasi
	@api.one
	def _get_button_persentase(self):
		self.persentase_negosiasi += len(self.negosiasi_line_ids)

	@api.multi
	def list_negosiasi(self):
		self.ensure_one()
		action = self.env.ref('adh_precast.action_adh_pre_pemasaran_negosisasi').read()[0]
		action['domain'] = [('penawaran_id','=',self.id)]				
		return action

		
		

	# Total Penjualan
	@api.depends('amount_untaxed')
	def _get_total_penjualan(self):
		for rec in self:							
			rec.total_penjualan = rec.amount_untaxed
					
	# Total Profit
	@api.depends('order_line')
	def _get_total_hpp_all(self):
		for rec in self:
			if rec.order_line:
				for line in rec.order_line:
					rec.total_hpp += ((line.total_hpp + line.total_biaya)* line.product_uom_qty)
				
	# Status Negosiasi
	@api.one
	@api.depends('state')
	def _get_status_negosiasi(self):
		for line in self:
			line.status_negosiasi = line.state

	# Total Biaya Langsung
	@api.depends('list_biaya')
	def _get_total_biaya_langsung(self):
		total_biaya = 0
		for rec in self:
			if rec.list_biaya:
				for x in rec.list_biaya:
					total_biaya += x.total_biaya
				rec.total_biaya_langsung = total_biaya
				
	# Total Biaya
	@api.depends('total_biaya_langsung','total_hpp')
	def _get_total_biaya(self):		
		for rec in self:
			rec.grand_total_biaya = rec.total_biaya_langsung + rec.total_hpp

	# Total Profit
	@api.depends('total_profit')
	def _get_total_profit(self):
		for rec in self:
			if rec.grand_total_biaya:
				rec.total_profit = rec.amount_untaxed - rec.grand_total_biaya

	@api.multi
	def button_evaluasi(self):
		evaluasi_obj = self.env['adhimix.mrp.evaluasi.penawaran']

		vals= evaluasi_obj.create({
		'no_penawaran'		: self.name,
		'tanggal_penawaran' : self.date_order,
		'nama_pelanggan'	: self.partner_id.id,
		'company_id'		: self.company_id.id,
		})
		return {
				  'name': ('Evaluasi Penawaran'),
				  'view_type': 'form',
				  'view_mode': 'form',
				  'res_model': 'adhimix.mrp.evaluasi.penawaran',
				  'res_id': vals.id,
				  'type': 'ir.actions.act_window',
		}

	@api.multi
	def action_nego_line(self):
		return {
				  'name': ('Negosiasi'),
				  'view_type': 'form',
				  'view_mode': 'form',
				  'res_model': 'sale.order',
				  'res_id': self.id,
				  'type': 'ir.actions.act_window',
		}
	@api.multi
	def button_berita_acara(self, vals):
		self.state = 'berita acara'
		ir_model_data = self.env['ir.model.data']
		compose_form_id = ir_model_data.get_object_reference('adh_precast', 'create_adh_mrp_kontrak_wizard')[1]

		return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'adhimix.mrp.kontrak.wizard',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': {
	                'default_tanggal'				: fields.Date.today (),
	                'default_nama_pelanggan'		: self.partner_id.id,	                	                
	                'default_sale_id'				: self.id,
	            }
            }

	@api.multi
	def view_negosiasi(self):
		action = self.env.ref('adh_precast.action_adh_pre_pemasaran_negosisasi')
		res = self.env.ref('sale.view_order_form')
		result = action.read()[0]

		result['views'] = [(res and res.id or False, 'form')]
		result['res_id'] = self.id or False
		return result

	#COPY
	@api.multi
	def button_negosiasi(self):
		List_Biaya_lines = []
		Bom_Lines = []
		stressing_line = []
		pengiriman_line = []
		install_line = []
		order_line = []
		cost_line = []
		for rec in self:
			for x in self.list_biaya:
				List_Biaya_lines.append((0,0,{
					'nama_biaya'          	: x.nama_biaya.id,
					'jenis_biaya'			: x.jenis_biaya,
					'nilai_biaya'			: x.nilai_biaya,
					'total_biaya'			: x.total_biaya,
					'reference'				: rec.id
				}))
				
			for res in self.order_line:
				if res.is_produksi == True:
					for line in res.bom_list:
						Bom_Lines.append((0,0,{
							'product_id'	: line.product_id.id,
							'satuan_barang' : line.product_id.uom_id.id,
							'qty'			: line.qty,
							'price_unit'	: line.product_id.standard_price,
							'reference'		: res.id,
						}))
				if res.is_stressing == True:
					for stressing in res.stressing_list_ids:
						stressing_line.append((0,0,{
							'product_id'	 : stressing.product_id.id,				
							'product_qty'	 : stressing.product_qty,
							'koefisien'		 : stressing.koefisien,
							'price_unit'	 : stressing.product_id.standard_price,							
							'reference'		 : res.id
							}))
				if res.is_pengiriman == True:
					for pengiriman in res.pengiriman_list_ids:
						pengiriman_line.append((0,0,{
							'product_id'	 : pengiriman.product_id.id,				
							'product_qty'	 : pengiriman.product_qty,
							'koefisien'		 : pengiriman.koefisien,
							'price_unit'	 : pengiriman.product_id.standard_price,							
							'reference'		 : res.id
							}))
				if res.is_install == True:
					for install in res.install_list_ids:
						install_line.append((0,0,{
							'product_id'	 : install.product_id.id,				
							'product_qty'	 : install.product_qty,
							'koefisien'		 : install.koefisien,
							'price_unit'	 : install.product_id.standard_price,							
							'reference'		 : res.id
						
							}))
				for cost in res.cost_list :
					cost_line.append((0,0,{
						'nama_biaya' : cost.nama_biaya.id,
						'nilai_biaya' : cost.nilai_biaya,
						'reference' : res.id
						}))

				order_line.append((0,0,{
					'order_id'			: rec.id,
					'product_id'		: res.product_id.id,
					'product_uom_qty'	: res.product_uom_qty,
					'product_uom'		: res.product_uom.id,
					'price_unit'		: res.price_unit,
					'is_produksi'		: res.is_produksi,
					'is_install'		: res.is_install,
					'is_stressing'		: res.is_stressing,
					'is_pengiriman'		: res.is_pengiriman,
					'jenis_produk'		: res.jenis_produk,
					'organisasi'		: res.organisasi.id,
					'cost_list'			: cost_line,
					'bom_list'			: Bom_Lines,
					'install_list_ids' 	: install_line,
					'pengiriman_list_ids' : pengiriman_line,
					'stressing_list_ids' : stressing_line
					}))


			negosisasi_id = rec.copy({
				'penawaran_id'					: self.id,
				'is_negosiasi'					: True,
				'state'							: 'sent',
				'list_biaya'					: List_Biaya_lines,
				'order_line' 					: order_line,
				})

			# print "============================"
			# print 'bom_list:',Bom_Lines
			# # print "product_id :" ,line.product_id.id
			# # print "satuan_barang :" ,line.product_id.uom_id,
			# # print "qty :" ,line.qty
			# # print "price_unit :" ,line.product_id.standard_price
			# # print "reference :" ,res.id
			# print '============================'
		

			return negosisasi_id.view_negosiasi()

	@api.multi
	def action_confirm(self):
		for order in self:
			order.state = 'sale'
			order.confirmation_date = fields.Datetime.now()
			if self.env.context.get('send_email'):
				self.force_quotation_send()
			order.order_line._action_procurement_create()
		if self.env['ir.values'].get_default('sale.config.settings', 'auto_done_setting'):
			self.action_done()
		# Rubah status nego yang lain
		sale_obj = self.search(['|', ('penawaran_id','=',self.penawaran_id.id),('id','=',self.penawaran_id.id)])
		for x in sale_obj:
			if x.state == 'sent':
				x.write({'state':'cancel'}) 
			elif x.state == 'draft':				
				x.write({'state':'cancel'}) 

		if not self.validity_date:
			raise Warning('Harap Isi Expiration Date !!!')
		elif not self.nama_proyek_id:
			raise Warning('Harap Isi Nama Proyek !!!')
		for res in self.order_line:			
				# Create Cost Control
			cost_control_obj = self.env['adhimix.pre.cost.control'].create({
																	'product_id' : res.product_id.id,
																	'kontrak_id' : self.id,
																	'pelanggan'  : self.partner_id.id,
																	'nama_proyek_id' : self.nama_proyek_id.id,
																	'deadline_kontrak' : self.validity_date,
																	'sisa_rap'		: res.product_uom_qty,
																	'total_rap'		: res.product_uom_qty,
																	'company_id'	: self.company_id.id
																	})
			res.cost_control_id = cost_control_obj.id
			for biaya in self.list_biaya:
				cost_line_obj = self.env['adhimix.pre.cost.control.line'].create({
																		'reference'		: cost_control_obj.id,
																		# 'name'		: cost_control_obj.id,
																		'uraian_id'	: biaya.nama_biaya.name,
																		'jumlah_volume_hpp' : 1,
																		# 'satuan_volume_hpp' : bom.satuan_barang.id,
																		'harga_hpp'			: biaya.total_biaya,
																		'total_harga_hpp'	: biaya.total_biaya,
																		'harga_realisasi'	: biaya.total_biaya

																		})
			# if res.is_produksi == True:
			for bom in res.bom_list:				
				cost_line_obj = self.env['adhimix.pre.cost.control.line'].create({
																	'reference'		: cost_control_obj.id,
																	# 'name'		: cost_control_obj.id,
																	'uraian_id'	: bom.product_id.name,
																	'jumlah_volume_hpp' : bom.qty,
																	'satuan_volume_hpp' : bom.satuan_barang.id,
																	'harga_hpp'			: bom.price_unit,
																	'total_harga_hpp'	: bom.price_subtotal,
																	'satuan_volume_realisasi' : bom.satuan_barang.id,
																	'harga_realisasi'		: bom.price_unit

																	})
		# elif res.is_pengiriman == True:
			for pengiriman in res.pengiriman_list_ids:				
				cost_line_obj = self.env['adhimix.pre.cost.control.line'].create({
																	'reference'		: cost_control_obj.id,
																	# 'name'		: cost_control_obj.id,
																	'uraian_id'	: pengiriman.product_id.name,
																	'jumlah_volume_hpp' : pengiriman.total,
																	'satuan_volume_hpp' : pengiriman.product_id.uom_id.id,
																	'harga_hpp'			: pengiriman.price_unit,
																	'total_harga_hpp'	: pengiriman.total_harga,
																	'satuan_volume_realisasi' : pengiriman.product_id.uom_id.id,
																	'harga_realisasi'		: pengiriman.price_unit

																	})
		# elif res.is_stressing == True:
			for stressing in res.stressing_list_ids:				
				cost_line_obj = self.env['adhimix.pre.cost.control.line'].create({
																	'reference'		: cost_control_obj.id,
																	# 'name'		: cost_control_obj.id,
																	'uraian_id'	: stressing.product_id.name,
																	'jumlah_volume_hpp' : stressing.total,
																	'satuan_volume_hpp' : stressing.product_id.uom_id.id,
																	'harga_hpp'			: stressing.price_unit,
																	'total_harga_hpp'	: stressing.total_harga,
																	'satuan_volume_realisasi' : stressing.product_id.uom_id.id,
																	'harga_realisasi'		: stressing.price_unit

																	})
			# elif res.is_install == True:
			for install in res.install_list_ids:				
				cost_line_obj = self.env['adhimix.pre.cost.control.line'].create({
																	'reference'		: cost_control_obj.id,
																	# 'name'		: cost_control_obj.id,
																	'uraian_id'	: install.product_id.name,
																	'jumlah_volume_hpp' : install.total,
																	'satuan_volume_hpp' : pengiriman.product_id.uom_id.id,
																	'harga_hpp'			: install.price_unit,
																	'total_harga_hpp'	: install.total_harga,
																	'satuan_volume_realisasi' : install.product_id.uom_id.id,
																	'harga_realisasi'		: install.price_unit

																	})

			

	@api.multi
	def action_spp(self):
		ir_model_data = self.env['ir.model.data']
		compose_form_id = ir_model_data.get_object_reference('adh_precast', 'create_adh_pre_spp_wizard')[1]
		order_line = []
		spp_lines = []
		for data in self.order_line :
			order_line.append({
				'product_id': data.product_id.id,
				'satuan_barang': data.product_uom.id,
				'batas_produksi': data.batas_produksi,
				# 'product_qty': data.product_uom_qty,
				})
			# for x in line.spp_lines:
			# 	spp_lines.append((0,0,{
			# 			'spp_id' : x.spp_id.id,
			# 			'plant_id' : x.plant_id.id,
			# 			'tanggal_pembuatan' : x.tanggal_pembuatan
			# 	}))
			print '========================'
			print 'LIHAT ORDER LINE',order_line
			print '========================'
	        return {
		            'type': 'ir.actions.act_window',
		            'view_type': 'form',
		            'view_mode': 'form',
		            'res_model': 'adhimix.pre.create.spp.wizard',
		            'views': [(compose_form_id, 'form')],
		            'view_id': compose_form_id,
		            'target': 'new',
		            'context': {
		                'default_kontrak_id': self.id,
		                'default_plant_id': self.company_id.id,
		                'default_plant_produksi_id': self.company_id.id,
		                'default_nama_proyek_id': self.nama_proyek_id.id,
		                'default_order_lines': order_line,
		                'default_tanggal_pembuatan': fields.Date.today (),		                
		            }
		        }

		# Create SPP
		# spp_id = self.env['adhimix.pre.spp'].create({															
		# 											# 'sale_id': self.id,
		# 											'kontrak_id': self.id,
		# 											'nama_proyek_id' : self.nama_proyek_id.id,
		# 											'tanggal': self.date_order,																								
		# 											})
		
		
		# self.spp_id = spp_id.id
		# for line in self.order_line:
		# 	# Create SPP Line
		# 	spp_product_id = self.env['adhimix.pre.spp.line'].create({																		
		# 															'reference' : spp_id.id,
		# 															'name' : line.product_id.name, 
		# 															'product_id' : line.product_id.id,
		# 															'satuan_barang' : line.product_id.uom_id.id,
		# 															'qty' : line.product_uom_qty,
		# 															'price_unit' : line.price_subtotal, 
		# 															})						
		
			
		return True
	
	@api.multi
	def action_bom(self):		
		if self.order_line:
			for line in self.order_line:
				#Remove Old List
				if line.bom_list:
					for bom in line.bom_list:
						bom.unlink()
						
				if line.bom_id and line.bom_id.bom_line_ids:
					for bom_line in line.bom_id.bom_line_ids:
						if bom_line.product_id.bom_ids:
							if bom_line.product_id.bom_ids.bom_line_ids:
								for detail in bom_line.product_id.bom_ids.bom_line_ids:
									self.env['sale.order.line.bom'].create({
																		'sale_id' : self.id,
																		'reference' : line.id, 
																		'product_id' : detail.product_id.id,
																		'satuan_barang' : detail.product_id.uom_id.id,
																		'qty' : detail.product_qty,
																		'price_unit' : detail.product_id.standard_price,
																		})
						else:
							self.env['sale.order.line.bom'].create({
																	'sale_id' : self.id,
																	'reference' : line.id, 
																	'product_id' : bom_line.product_id.id,
																	'satuan_barang' : bom_line.product_id.uom_id.id,
																	'qty' : bom_line.product_qty,
																	'price_unit' : bom_line.product_id.standard_price,
																	})
	

class SaleOrderLineCost(models.Model):
	_name = "sale.order.line.cost"
		
	reference = fields.Many2one(comodel_name="sale.order.line",string="Reference")	
	nama_biaya = fields.Many2one(comodel_name="adhimix.biaya",string="Nama Biaya")	
	nilai_biaya = fields.Float(string="Nilai Biaya")			
									
class SaleOrderLine(models.Model):
	_inherit = "sale.order.line"
	
	total_biaya_sales = fields.Float(compute="_get_total_biaya_sales", string="Pembebanan")
	total_hpp = fields.Float(compute="_get_total_hpp", string="HPP")
	total_biaya = fields.Float(compute="_get_total_biaya", string="Biaya Persiapan")
	total_biaya_hpp = fields.Float(compute="_get_total_biaya_hpp", string="Total Biaya")
	total_margin = fields.Float(compute="_get_total_margin", string="Margin")
	total_profit = fields.Float(compute="_get_total_profit", string="Profit")	
	is_margin = fields.Boolean(string="Set Margin", default=False)
	nilai_margin = fields.Float(string="Margin")
	volume_spp = fields.Float("Volume SPP",compute="_get_volume_spp",store=True)
	volume_produksi = fields.Float("Volume Produksi")
	persentase_produksi = fields.Float("Persentase Produksi")
	volume_kirim = fields.Float("Volume Kirim")
	persentase_kirim = fields.Float("Persentase Kirim")
	volume_stressing = fields.Float("Volume Stressing")
	persentase_stressing = fields.Float("Persentase Stressing")
	volume_install = fields.Float("Volume Install")
	persentase_install = fields.Float("Persentase Install")
	bom_id = fields.Many2one(comodel_name="mrp.bom",string="BOM")
	bom_list = fields.One2many(comodel_name="sale.order.line.bom",inverse_name="reference",string="Komponen BOM")
	cost_list = fields.One2many(comodel_name="sale.order.line.cost",inverse_name="reference",string="Komponen Biaya")						
	stressing_list_ids = fields.One2many('sale.order.line.bom.stressing','reference','Stressing')
	pengiriman_list_ids = fields.One2many('sale.order.line.bom.pengiriman','reference','Pengiriman')
	install_list_ids = fields.One2many('sale.order.line.bom.install','reference','Install')
	is_produksi = fields.Boolean("Produksi",default=True)
	is_stressing = fields.Boolean("Stressing",default=False)
	is_pengiriman = fields.Boolean("Pengiriman",default=False)
	is_install = fields.Boolean("Install",default=False)	
	reference = fields.Many2one(comodel_name="sale.order",string="Reference")
	uraian_id  = fields.Many2one(comodel_name="sale.order.line.detail.uraian",string="Uraian")
	cost_control_id = fields.Many2one('adhimix.pre.cost.control','Cost Control')
	spp_lines = fields.One2many('adhimix.pre.daftar.spp.line','reference','Daftar SPP')
	batas_produksi = fields.Float("Batas Produksi",compute="_get_batas_produksi",store=True)
	jenis_produk = fields.Selection([('Infrastucture','Infrastucture'),('Gedung','Gedung')
									,('Understructure','Understructure'),('Beton','Beton')],string="Jenis Produk")
	organisasi = fields.Many2one('res.company','Organisasi')


	@api.one
	@api.depends('product_uom_qty','batas_produksi')
	def _get_volume_spp(self):
		self.volume_spp = self.product_uom_qty - self.batas_produksi




	@api.onchange('bom_id')
	def onchange_bom_id(self):
		bom_list = []

		for data in self.bom_id.bom_line_ids :
			# for line in self.bom_list:
			bom_list.append({
				# 'reference'				: self.id,
				'product_id'          	: data.product_id.id,
				'satuan_barang'			: data.product_uom_id.id,
				'qty'					: data.product_qty,
				'price_unit'			: data.product_id.standard_price,
				# 'price_subtotal'		: line.price_subtotal
			})
			# print 'AAAAAAAAAAAAAAaa',data
		return {'value': {
	      'bom_list': bom_list,
	    }}

	@api.onchange('nilai_margin')
	def onchange_nilai_margin(self):		
		if self.nilai_margin:			
			self.price_unit = self.total_biaya_hpp + (self.total_biaya_hpp * self.nilai_margin / 100)

	@api.one
	@api.depends('total_biaya','total_hpp','price_unit')
	def _get_total_margin(self):
		for rec in self:
			if rec.price_unit > 0:						
				rec.total_margin = ((rec.price_unit - rec.total_biaya_hpp) / rec.price_unit) * 100
			
	@api.one
	@api.depends('total_biaya_hpp','price_unit')
	def _get_total_profit(self):
		for rec in self:						
			rec.total_profit = rec.price_unit - rec.total_biaya_hpp			
				
	@api.one
	@api.depends('order_id.list_biaya','price_unit')
	def _get_total_biaya_sales(self):		
		for rec in self:
			for biaya in rec.order_id.list_biaya:
				if biaya.jenis_biaya == "Nominal":				
					rec.total_biaya_sales += biaya.total_biaya
				elif biaya.jenis_biaya == "Persentase":				
					rec.total_biaya_sales += (biaya.nilai_biaya * rec.price_unit / 100)			
				
	@api.one
	@api.depends('bom_list','is_produksi','stressing_list_ids','is_stressing','pengiriman_list_ids','is_pengiriman','install_list_ids','is_install')
	def _get_total_hpp(self):		
		for rec in self:
			for bom in rec.bom_list:
				if rec.is_produksi == True:
					rec.total_hpp += bom.price_subtotal
			for stressing in rec.stressing_list_ids :
				if rec.is_stressing == True:
					rec.total_hpp += stressing.total_harga		
			for install in rec.install_list_ids:
				if rec.is_install == True:
					rec.total_hpp += install.total_harga
			for line in rec.pengiriman_list_ids :
				if rec.is_pengiriman == True:
					rec.total_hpp += line.total_harga
	
	@api.one	
	@api.depends('cost_list')
	def _get_total_biaya(self):		
		for rec in self:
			for cost in rec.cost_list:
				rec.total_biaya += (cost.nilai_biaya / rec.product_uom_qty)			
		
	@api.one	
	@api.depends('total_hpp','total_biaya','total_biaya_sales')
	def _get_total_biaya_hpp(self):
		for rec in self:				
			rec.total_biaya_hpp = rec.total_biaya + rec.total_hpp + rec.total_biaya_sales			
			
	@api.onchange('product_id')
	def onchange_product_id(self):
		bom_id = False				
		if self.product_id:					
			if self.product_id.product_tmpl_id.bom_ids:			
				bom_id = self.product_id.product_tmpl_id.bom_ids[0].id				
				self.bom_id = bom_id
				self.jenis_produk = self.product_id.jenis_produk

	@api.depends('product_uom_qty')
	def _get_batas_produksi(self):
		for res in self:
			res.batas_produksi = res.product_uom_qty
					
class sale_order_line_detail_uraian(models.Model):
	_name = "sale.order.line.detail.uraian"

	name = fields.Text("Uraian")

class SaleOrderLineBom(models.Model):
	_name = "sale.order.line.bom"
	
	sale_id = fields.Many2one(comodel_name="sale.order",string="Sales Order")
	reference = fields.Many2one(comodel_name="sale.order.line",string="Reference")	
	product_id = fields.Many2one(comodel_name="product.product",string="Nama Barang")
	satuan_barang = fields.Many2one(comodel_name="product.uom", string="Satuan Barang")
	qty = fields.Float(string="Qty")
	price_unit = fields.Float(string="Harga Satuan")
	price_subtotal = fields.Float(compute="_compute_price_subtotal", string="Total Harga")		
	
	@api.depends('price_unit', 'qty')
	def _compute_price_subtotal(self):
		for rec in self:
			rec.price_subtotal = rec.price_unit * rec.qty

class SaleOrderLineBomPengiriman(models.Model):
	_name = "sale.order.line.bom.pengiriman"

	reference = fields.Many2one('sale.order.line', string='Reference')
	product_id = fields.Many2one('product.product', string='Nama Produk')
	product_qty = fields.Float('Volume')
	price_unit = fields.Float( "Harga Satuan",compute="_get_price_unit")
	koefisien = fields.Float('Koefisien')
	total_harga = fields.Float("Total Harga",compute="_get_total_harga")
	total = fields.Float(compute="_get_total", string='Total')
		
	@api.depends('product_qty','koefisien')
	def _get_total(self):
		for res in self:		
			res.total = res.product_qty * res.koefisien
	
	@api.depends('product_id')
	def _get_price_unit(self):
		for res in self:
			res.price_unit = res.product_id.standard_price

	@api.depends('total','price_unit')
	def _get_total_harga(self):
		for res in self:
			res.total_harga = res.total * res.price_unit		
	
class SaleOrderLineBomStressing(models.Model):
	_name = "sale.order.line.bom.stressing"

	reference = fields.Many2one('sale.order.line', string='Reference')
	product_id = fields.Many2one('product.product', string='Nama Produk')
	product_qty = fields.Float('Volume')
	price_unit = fields.Float("Harga Satuan",compute="_get_price_unit")
	koefisien = fields.Float("Koefisien")
	total = fields.Float(compute="_get_total", string='Total')
	total_harga = fields.Float("Total Harga",compute="_get_total_harga",)
	
	@api.depends('product_qty','koefisien')
	def _get_total(self):
		for res in self:		
			res.total = res.product_qty * res.koefisien
	
	@api.depends('product_id')
	def _get_price_unit(self):
		for res in self:
			res.price_unit = res.product_id.standard_price

	@api.depends('total','price_unit')
	def _get_total_harga(self):
		for res in self:
			res.total_harga = res.total * res.price_unit

class SaleOrderLineBomInstall(models.Model):
	_name = "sale.order.line.bom.install"

	reference = fields.Many2one('sale.order.line', string='Reference')
	product_id = fields.Many2one('product.product', string='Nama Produk')
	product_qty = fields.Float('Volume')
	price_unit = fields.Float("Harga Satuan",compute="_get_price_unit")
	koefisien = fields.Float('Koefisien')
	total = fields.Float(compute="_get_total", string='Total')
	total_harga = fields.Float("Total Harga",compute="_get_total_harga",)

	@api.depends('product_qty','koefisien')
	def _get_total(self):
		for res in self:		
			res.total = res.product_qty * res.koefisien
	
	@api.depends('product_id')
	def _get_price_unit(self):
		for res in self:
			res.price_unit = res.product_id.standard_price

	@api.depends('total','price_unit')
	def _get_total_harga(self):
		for res in self:
			res.total_harga = res.total * res.price_unit


class AdhPreDaftarSpp(models.Model):
	_name = 'adhimix.pre.daftar.spp.line'

	reference = fields.Many2one('sale.order.line','reference')
	spp_id = fields.Many2one('adhimix.pre.spp','Nomor SPP')
	plant_id = fields.Many2one('res.company','Plant')
	tanggal_pembuatan = fields.Date(string="Tanggal Pembuatan")

#Menu BA & Negosiasi 
# class adh_mrp_kontrak(models.Model):
# 	_name = "adhimix.mrp.kontrak"

# 	name = fields.Char("No Kontrak")
# 	sale_id = fields.Many2one(comodel_name="sale.order",string="Nomor Penawaran")
# 	tanggal = fields.Date("Tanggal")
# 	# tanggal_efektif = fields.Date("Tanggal Efektif",default=lambda self:time.strftime("%Y-%m-%d"))
# 	pekerjaan = fields.Text("Pekerjaan")
# 	lokasi = fields.Text("Lokasi")
# 	spesifikasi = fields.Text("Spesifikasi")
# 	waktu_pelaksanaan = fields.Date("Mulai Pelaksanaan")
# 	waktu_pelaksanaan_end = fields.Date("Selesai Pelaksanaan")
# 	harga_negosiasi = fields.Float("Harga Negosiasi")
# 	# cara_pembayaran = fields.Text("Cara Pembayaran")
# 	cara_pembayaran_id = fields.Many2one('adhimix.cara.Pembayaran',"Cara Pembayaran")
# 	scope_pekerjaan_owner = fields.Text("Scope Pekerjaan PT. API")
# 	scope_pekerjaan_client = fields.Text("Scope Pekerjaan Pelanggan")
# 	nama_pelanggan = fields.Many2one(comodel_name="res.partner",string="Nama Pelanggan")
# 	lampiran = fields.Many2many(comodel_name="ir.attachment",string="Lampiran")
# 	company_id = fields.Many2one(comodel_name="res.company",string="Company",default=lambda self:self.env.user,readonly=True)
# 	product_ids = fields.One2many(comodel_name="adhimix.mrp.kontrak.product",inverse_name="reference",string="List Product")	
	
# 	@api.model
# 	def create(self, vals):
# 		vals['name'] = self.env['ir.sequence'].next_by_code('adhimix.mrp.kontrak')
# 		return super(adh_mrp_kontrak, self).create(vals)

# class AdhimixMrpKontrakProduct(models.Model):
# 	_name = "adhimix.mrp.kontrak.product"
			
# 	reference = fields.Many2one(comodel_name="adhimix.mrp.kontrak",string="Reference")	
# 	product_id = fields.Many2one(comodel_name="product.product",string="Nama Barang")
# 	satuan_barang = fields.Many2one(comodel_name="product.uom", string="Satuan Barang")
# 	qty = fields.Float(string="Qty")
# 	price_unit = fields.Float(string="Unit Price")
# 	bom_ids = fields.One2many(comodel_name="adhimix.mrp.kontrak.product.bom",inverse_name="reference",string="Komponen BOM")
# 	price_subtotal = fields.Float(compute="_compute_price_subtotal_kontrak_product", string="Price Subtotal")		
	
# 	@api.depends('price_unit', 'qty')
# 	def _compute_price_subtotal_kontrak(self):
# 		for rec in self:
# 			rec.price_subtotal = rec.price_unit * rec.qty
	
# class AdhimixMrpKontrakProductBom(models.Model):
# 	_name = "adhimix.mrp.kontrak.product.bom"
		
# 	reference = fields.Many2one(comodel_name="adhimix.mrp.kontrak.product",string="Reference")	
# 	product_id = fields.Many2one(comodel_name="product.product",string="Nama Barang")
# 	satuan_barang = fields.Many2one(comodel_name="product.uom", string="Satuan Barang")
# 	qty = fields.Float(string="Qty")
# 	price_unit = fields.Float(string="Harga Satuan")
# 	price_subtotal = fields.Float(compute="_compute_price_subtotal_kontrak", string="Total Harga")		
	
# 	@api.depends('price_unit', 'qty')
# 	def _compute_price_subtotal_kontrak(self):
# 		for rec in self:
# 			rec.price_subtotal = rec.price_unit * rec.qty
	

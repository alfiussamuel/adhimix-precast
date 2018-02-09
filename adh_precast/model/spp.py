from odoo import api, fields, models, _
import time
import datetime
from datetime import date
from dateutil.rrule import rrule, DAILY


class adhimix_pre_spp(models.Model):
	_name = 'adhimix.pre.spp'

	name = fields.Char(string="Nomor Spp", readonly=True)
	kontrak_id = fields.Many2one('sale.order')
	plant_id = fields.Many2one('res.company','Plant')
	nama_proyek_id = fields.Many2one('project.project','Nama Proyek')
	tanggal = fields.Date("Tanggal Pembuatan SPP", required=True,default=lambda self:time.strftime("%Y-%m-%d"))
	product_list = fields.One2many(comodel_name="adhimix.pre.spp.line",inverse_name="reference",string="List Barang")
	rencana_produksi = fields.One2many(comodel_name="adhimix.pre.spp.rencana.produksi",inverse_name="reference",string="Rencana Produksi")
	rencana_pengiriman = fields.One2many(comodel_name="adhimix.pre.rencana.pengiriman",inverse_name="reference",string="Rencana Pengiriman")
	rencana_stressing = fields.One2many(comodel_name="adhimix.pre.rencana.stressing",inverse_name="reference",string="Rencana Stressing")
	rencana_install = fields.One2many(comodel_name="adhimix.pre.rencana.install",inverse_name="reference",string="Rencana Install")

	# Sequence
	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('adhimix.pre.spp')
		return super(adhimix_pre_spp, self).create(vals)

	@api.multi
	def action_simulasi(self,values):
		for rec in self:			
			delta = datetime.timedelta(days=1)
			x = 1
			y = 3
			d = date.now()
			while x <= y:				
				self.env['adhimix.pre.rencana.produksi'].create({
															'reference': rec.id,
															'tanggal_mulai': d
															})			    
				d += delta
				x += 1			


class adhimix_pre_spp_line(models.Model):
	_name ="adhimix.pre.spp.line"

	reference = fields.Many2one(comodel_name="adhimix.pre.spp",string="Reference")
	product_id = fields.Many2one(comodel_name="product.product",string="Nama Barang", required=True)
	satuan_barang = fields.Many2one(comodel_name="product.uom", required=True, string="Satuan Barang" )
	qty = fields.Float(string="Qty",required=True)

	@api.onchange('product_id')
	def onchange_product_id(self):
		self.satuan_barang = self.product_id.uom_id


class AdhimixPreSppRencanaProduksi(models.Model):
	_name = "adhimix.pre.spp.rencana.produksi"

	reference = fields.Many2one(comodel_name="adhimix.pre.spp",string="Reference")
	product_id = fields.Many2one(comodel_name="product.product",string="Nama Barang")
	line_produksi = fields.Many2one(comodel_name="adhimix.pre.line", string="Line Produksi")
	qty = fields.Float(string="Qty")
	tanggal_mulai= fields.Date(string="Tanggal Mulai")
	tanggal_selesai= fields.Date(string="Tanggal Selesai")
	nomor_mo = fields.Many2one(comodel_name="mrp.production",string="Nomor MO")
	qty_done = fields.Float(string="Qty Selesai")
	qty_cancel= fields.Float(string="Qty Batal")
	qty_remaining = fields.Float(string="Qty Sisa")
	qty_pindah = fields.Float(string="Qty Pindah")
	qty_pindahan = fields.Float(string="Qty Pindahan")


class adhimix_pre_rencana_pengiriman(models.Model):
	_name = 'adhimix.pre.rencana.pengiriman'

	reference = fields.Many2one(comodel_name="adhimix.pre.spp", string="Reference")
	product_id = fields.Many2one(comodel_name="product.product", string="Nama Barang")
	qty = fields.Float(string="Qty")
	nomor_do = fields.Many2one(comodel_name="stock.picking", string="Nomor DO")
	jadwal_kirim = fields.Date(string="Jadwal Kirim")
	tanggal_kirim = fields.Date(string="Tanggal Kirim")
	qty_done = fields.Float(string="Qty Selesai")
	qty_cancel = fields.Float(string="Qty Batal")
	qty_repair = fields.Float(string="Repair")
	qty_reject = fields.Float(string="Reject")


class adhimix_pre_rencana_stressing(models.Model):
	_name = 'adhimix.pre.rencana.stressing'

	reference = fields.Many2one(comodel_name="adhimix.pre.spp", string="Reference")
	product_id = fields.Many2one(comodel_name="product.product", string="Nama Barang")
	qty = fields.Float(string="Qty")
	jadwal_stressing = fields.Date(string="Jadwal Stressing")
	tanggal_stressing = fields.Date(string="Tanggal Stressing")
	qty_done = fields.Float(string="Qty Selesai")
	qty_cancel = fields.Float(string="Qty Batal")
	qty_repair = fields.Float(string="Repair")
	qty_reject = fields.Float(string="Reject")


class adhimix_pre_rencana_install(models.Model):
	_name = 'adhimix.pre.rencana.install'

	reference = fields.Many2one(comodel_name="adhimix.pre.spp", string="Reference")
	product_id = fields.Many2one(comodel_name="product.product", string="Nama Barang")
	qty = fields.Float(string="Qty")
	jadwal_install = fields.Date(string="Jadwal Install")
	tanggal_install = fields.Date(string="Tanggal Install")
	qty_done = fields.Float(string="Qty Selesai")
	qty_cancel = fields.Float(string="Qty Batal")
	qty_repair = fields.Float(string="Repair")
	qty_reject = fields.Float(string="Reject")

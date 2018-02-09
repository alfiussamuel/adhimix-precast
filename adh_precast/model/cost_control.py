from odoo import api,fields,models,_ 
import time
		
		
class AdhimixPreCostControl(models.Model):
	_name = "adhimix.pre.cost.control"
	_description = 'Cost Control'


	name = fields.Char(string="No Cost Control",readonly=True)
	product_id = fields.Many2one("product.product", "Product")
	# kontrak_id = fields.Many2one("adhimix.mrp.kontrak", "No. Kontrak")
	kontrak_id = fields.Many2one("sale.order", "No. Kontrak")
	pelanggan = fields.Many2one("res.partner", "Pelanggan")
	nama_proyek_id = fields.Many2one('project.project',"Nama Proyek")
	deadline_kontrak = fields.Date("Deadline Kontrak",required=True)
	subkon = fields.Many2one(comodel_name="res.partner",string="Subkon",domain=[('supplier','=',True)])
	id_cost_control = fields.Char("ID Cost Control")
	tanggal_efektif = fields.Date("Tanggal Efektif",default=lambda self:time.strftime("%Y-%m-%d"))
	company_id = fields.Many2one(comodel_name="res.company",string="Company")
	sisa_rap = fields.Float('Sisa RAP')
	total_rap = fields.Float('Total RAP')
	cost_control_ids = fields.One2many(comodel_name="adhimix.pre.cost.control.line",inverse_name="reference",string="Reference")
	state = fields.Selection([('Draft','Draft'),('Approved','Approved')],'State',default='Draft')
	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('adhimix.pre.cost.control')
		return super(AdhimixPreCostControl, self).create(vals)

	# Nyari nomer cost control + nama produk bila ada field many2one ke tabel ini
	@api.multi
	def name_get(self):
		res = []
		for rec in self:
			if rec.name and rec.product_id:
				name = rec.product_id.name
				res.append(( rec.id,name))
			elif rec.name and not rec.product_id:	
				nama = rec.name
				res.append((rec.id, nama ))
		return res



	

class AdhimixPreCostControlLine(models.Model):
	_name ="adhimix.pre.cost.control.line"

	reference = fields.Many2one(comodel_name="adhimix.pre.cost.control",string="No Cost Control")
	name = fields.Char("No Cost Control")
	# uraian_id = fields.Many2one(comodel_name="product.product",string="Produk")
	uraian_id = fields.Char(string="Uraian")
	spesifikasi = fields.Char("Spesifikasi")
	om_biaya = fields.Float("O/M Biaya")
	om_jumlah = fields.Float("O/M Jumlah")

	# Rencana HPP
	jumlah_volume_hpp = fields.Float("Total Volume Rencana")
	satuan_volume_hpp = fields.Many2one(string="Satuan Volume",comodel_name="product.uom")
	harga_hpp = fields.Float("Harga")
	total_harga_hpp = fields.Float("Total HPP")


	# Realisasi Saat ini
	jumlah_volume_realisasi = fields.Float("Total Volume Realisasi")
	satuan_volume_realisasi =fields.Many2one(string="Satuan Volume",comodel_name="product.uom")
	harga_realisasi = fields.Float("Harga")
	total_harga_realisasi = fields.Float("Total Realisasi")

	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('adhimix.pre.cost.control.line')
		return super(AdhimixPreCostControlLine, self).create(vals)
	
	@api.onchange('jumlah_volume_hpp','harga_hpp','total_harga_hpp')
	def onchange_total_harga_hpp(self):
		self.total_harga_hpp =(self.jumlah_volume_hpp * self.harga_hpp)

	@api.onchange('jumlah_volume_realisasi','harga_realisasi','total_harga_realisasi')
	def onchange_total_harga_realisasi(self):
		self.total_harga_realisasi =(self.jumlah_volume_realisasi * self.harga_realisasi)


	
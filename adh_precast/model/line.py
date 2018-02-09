from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AdhimixPreLineActive(models.Model):
	_name = 'adhimix.pre.line.active'

	reference = fields.Many2one("adhimix.pre.line", required=True, string="Line ID")
	nomor_mo = fields.Many2one(comodel_name="mrp.production", required=True, string="Nomor MO")
	qty_produksi = fields.Float(string="Qty Produksi", required=True)
	tanggal = fields.Date(string="Tanggal")
	status_produksi = fields.Char(string="Status Produksi", compute="_get_status_produksi")

	@api.depends('status_produksi')
	def _get_status_produksi(self):
		for rec in self:
			rec.status_produksi = rec.nomor_mo.state


class AdhimixPreLineDone(models.Model):
	_name = 'adhimix.pre.line.done'

	reference = fields.Many2one("adhimix.pre.line", required=True, string="Line ID")
	nomor_mo = fields.Many2one(comodel_name="mrp.production", required=True, string="Nomor MO")
	qty_produksi = fields.Float(string="Qty Produksi", required=True)
	tanggal = fields.Date(string="Tanggal")
	status_produksi = fields.Char(string="Status Produksi", compute="_get_status_produksi")

	@api.depends('status_produksi')
	def _get_status_produksi(self):
		for rec in self:
			rec.status_produksi = rec.nomor_mo.state


class AdhimixPreLine(models.Model):
	_name = 'adhimix.pre.line'

	name = fields.Char(string="Nama Line", readonly=True)
	satuan_barang = fields.Many2one(comodel_name="product.uom", required=True, string="Satuan Barang")
	kapasitas_line = fields.Float(string="Kapasitas Per Hari", required=True)
	dibuat_oleh = fields.Many2one(comodel_name="res.users", readonly=True, string="Dibuat Oleh", default=lambda self: self._uid)
	produksi_berjalan = fields.One2many("adhimix.pre.line.active", "reference", "Produksi Berjalan")
	produksi_selesai = fields.One2many("adhimix.pre.line.done", "reference", "Produksi Selesai")	
	
	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('adhimix.pre.line')		
		return super(AdhimixPreLine, self).create(vals)	

class MrpProduction(models.Model):
	_inherit = 'mrp.production'

	line_produksi = fields.Many2one(comodel_name="adhimix.pre.line", required=True, string="Line Produksi")

	# Inherit Function
	@api.model
	def create(self, values):
		if values['product_qty'] < self.env['adhimix.pre.line'].browse(values['line_produksi']).kapasitas_sisa:
			if values['product_uom_id'] == self.env['adhimix.pre.line'].browse(values['line_produksi']).satuan_barang.id:

				production = super(MrpProduction, self).create(values)				
				self.env["adhimix.pre.line.active"].create({
															'reference': production.line_produksi.id,
															'nomor_mo' : production.id,
															'qty_produksi' : production.product_qty,
															'tanggal' : production.date_planned_start,
															'status_produksi' : production.state
															}).id
			else :
				raise UserError(_('Satuan Uom harus sama dengan satuan line'))					
		else :
			raise UserError(_('Kapasitas sisa line tidak mencukupi'))
		return production


	@api.multi
	def button_mark_done(self):
		super(MrpProduction, self).button_mark_done()
		for production in self:
			self.env["adhimix.pre.line.done"].create({
													'reference': production.line_produksi.id,
													'nomor_mo' : production.id,
													'qty_produksi' : production.product_qty,
													'tanggal' : production.date_planned_start,
													'status_produksi' : production.state
													}).id

			active_mo = self.env['adhimix.pre.line.active'].search([('nomor_mo','=',production.id), ('reference','=',production.line_produksi.id)])
			if active_mo:
				active_mo.unlink()

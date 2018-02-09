from odoo import api,fields,models,_
import time
from odoo.exceptions import UserError, RedirectWarning, ValidationError, except_orm, Warning

class AdhimixBomPengiriman(models.Model):
	_name = "adhimix.bom.pengiriman"

	reference = fields.Many2one('mrp.bom', string='Reference')
	product_id = fields.Many2one('product.product', string='Nama Produk')
	product_qty = fields.Float('Volume', default=1)
	product_uom = fields.Many2one(compute='_get_product_uom', comodel_name='product.uom', string='Satuan')
	koefisien = fields.Float('Koefisien', default=1)
	total = fields.Float(compute="_get_total", string='Total')
	
	@api.depends('koefisien','product_qty')
	def _get_total(self):		
		for res in self:		
			res.total = res.product_qty * res.koefisien
			
	@api.depends('product_id')
	def _get_product_uom(self):		
		for res in self:		
			res.product_uom = res.product_id.uom_id.id	
	
class AdhimixBomStressing(models.Model):
	_name = "adhimix.bom.stressing"

	reference = fields.Many2one('mrp.bom', string='Reference')
	product_id = fields.Many2one('product.product', string='Nama Produk')
	product_qty = fields.Float('Volume', default=1)
	product_uom = fields.Many2one(compute='_get_product_uom', comodel_name='product.uom', string='Satuan')
	koefisien = fields.Float('Koefisien', default=1)
	total = fields.Float(compute="_get_total", string='Total')
	
	@api.depends('koefisien','product_qty')
	def _get_total(self):		
		for res in self:		
			res.total = res.product_qty * res.koefisien
			
	@api.depends('product_id')
	def _get_product_uom(self):		
		for res in self:		
			res.product_uom = res.product_id.uom_id.id
	
class AdhimixBomInstall(models.Model):
	_name = "adhimix.bom.install"

	reference = fields.Many2one('mrp.bom', string='Reference')
	product_id = fields.Many2one('product.product', string='Nama Produk')
	product_qty = fields.Float('Volume', default=1)
	product_uom = fields.Many2one(compute='_get_product_uom', comodel_name='product.uom', string='Satuan')
	koefisien = fields.Float('Koefisien', default=1)
	total = fields.Float(compute="_get_total", string='Total')
	
	@api.depends('koefisien','product_qty')
	def _get_total(self):		
		for res in self:		
			res.total = res.product_qty * res.koefisien
			
	@api.depends('product_id')
	def _get_product_uom(self):		
		for res in self:		
			res.product_uom = res.product_id.uom_id.id
	
class AdhimixProductBomType(models.Model):
	_name = "adhimix.product.bom.type"

	name = fields.Char('Tipe Produk BOM')	

class MrpBom(models.Model):
	_inherit = "mrp.bom"

	tipe_bom = fields.Selection([('Standar','Standar'),('Proyek','Proyek')], string='Tipe BOM')
	pengiriman_ids = fields.One2many('adhimix.bom.pengiriman', 'reference', 'HPP Pengiriman')
	stressing_ids = fields.One2many('adhimix.bom.stressing', 'reference', 'HPP Stressing')
	install_ids = fields.One2many('adhimix.bom.install', 'reference', 'HPP Install')
	
class MrpBomLine(models.Model):
	_inherit = "mrp.bom.line"

	bom_type = fields.Many2one('adhimix.product.bom.type', 'Tipe Produk BOM')
	koefisien = fields.Float('Koefisien', default=1)
	price_unit = fields.Float("Harga Satuan",compute="_get_price_unit")
	total = fields.Float(compute="_get_total", string='Total')
	subtotal = fields.Float("Total",compute="_get_subtotal")
	
	@api.depends('koefisien','product_qty')
	def _get_total(self):
		for res in self:		
			res.total = res.product_qty * res.koefisien							

	@api.depends('product_id')
	def _get_price_unit(self):
		for res in self:
			res.price_unit = res.product_id.standard_price	

	@api.depends('price_unit','product_qty')
	def _get_subtotal(self):
		for res in self:		
			res.subtotal = res.product_qty * res.price_unit					
	
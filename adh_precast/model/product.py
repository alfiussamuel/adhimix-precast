from odoo import api,fields,models,_
import time
from odoo.exceptions import UserError, RedirectWarning, ValidationError, except_orm, Warning
		
	
class ProductTemplate(models.Model):
	_inherit = "product.template"

	bom_type = fields.Many2one('adhimix.product.bom.type', 'Tipe Produk BOM')
	jenis_produk = fields.Selection([('Infrastucture','Infrastucture'),('Gedung','Gedung')
									,('Understructure','Understructure'),('Beton','Beton')],string="Jenis Produk")
	# level_id = fields.Many2one('adhimix.product.level', 'Kelompok Produk')
	# type_id = fields.Many2one('adhimix.product.type', 'Jenis Produk')
	
	# @api.onchange('level_id')
	# def onchange_level_id(self):
	# 	for res in self:
	# 		res.name = res.level_id.name		
	
# class AdhimixProductLevelSatu(models.Model):
# 	_name = "adhimix.product.level.satu"

# 	name = fields.Char('Nama Barang')				

# class AdhimixProductLevelDua(models.Model):
# 	_name = "adhimix.product.level.dua"

# 	name = fields.Char('Nama Barang')	
# 	parent_id = fields.Many2one('adhimix.product.level.satu', 'Parent')
# 	uom_id = fields.Many2one('product.uom', 'Satuan')
# 	#level = fields.Integer(compute="_get_level", string='Level')	
	
# 	@api.onchange('parent_id')
# 	def onchange_parent_id(self):
# 		for res in self:			
# 			if res.parent_id:
# 				res.name = res.parent_id.name
			
# 	#===========================================================================
# 	# @api.depends('parent_id')
# 	# def _get_level(self):
# 	# 	for res in self:
# 	# 		if not res.parent_id:
# 	# 			res.level = 1
# 	# 		elif res.parent_id:
# 	# 			res.level = res.parent_id.level + 1
# 	# 			res.name = res.parent_id.name
# 	#===========================================================================
				
# class AdhimixProductLevelTiga(models.Model):
# 	_name = "adhimix.product.level.tiga"

# 	name = fields.Char('Nama Barang')	
# 	parent_id = fields.Many2one('adhimix.product.level.dua', 'Parent')
# 	uom_id = fields.Many2one('product.uom', 'Satuan')
# 	#level = fields.Integer(compute="_get_level", string='Level')	
	
# 	@api.onchange('parent_id')
# 	def onchange_parent_id(self):
# 		for res in self:
# 			if res.parent_id:
# 				res.uom_id = res.parent_id.uom_id.id
# 			if res.parent_id:
# 				res.name = res.parent_id.name
			
# 	#===========================================================================
# 	# @api.depends('parent_id')
# 	# def _get_level(self):
# 	# 	for res in self:
# 	# 		if not res.parent_id:
# 	# 			res.level = 1
# 	# 		elif res.parent_id:
# 	# 			res.level = res.parent_id.level + 1
# 	# 			res.name = res.parent_id.name
# 	#===========================================================================

# class AdhimixProductLevel(models.Model):
# 	_name = "adhimix.product.level"

# 	name = fields.Char('Nama Barang')	
# 	parent_id = fields.Many2one('adhimix.product.level', 'Parent')
# 	uom_id = fields.Many2one('product.uom', 'Satuan')
# 	level = fields.Integer(compute="_get_level", string='Level')	
	
# 	@api.onchange('parent_id')
# 	def onchange_parent_id(self):
# 		for res in self:
# 			if res.parent_id:
# 				res.uom_id = res.parent_id.uom_id.id
# 			if res.parent_id:
# 				res.name = res.parent_id.name
			
# 	@api.depends('parent_id')
# 	def _get_level(self):
# 		for res in self:
# 			if not res.parent_id:
# 				res.level = 1
# 			elif res.parent_id:
# 				res.level = res.parent_id.level + 1
# 				res.name = res.parent_id.name
# 	
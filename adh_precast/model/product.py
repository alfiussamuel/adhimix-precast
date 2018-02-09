from odoo import api,fields,models,_
import time
from odoo.exceptions import UserError, RedirectWarning, ValidationError, except_orm, Warning
		
	
class ProductTemplate(models.Model):
	_inherit = "product.template"

	bom_type = fields.Many2one('adhimix.product.bom.type', 'Tipe Produk BOM')
	jenis_produk = fields.Selection([('Infrastucture','Infrastucture'),('Gedung','Gedung')
									,('Understructure','Understructure'),('Beton','Beton')],string="Jenis Produk")	
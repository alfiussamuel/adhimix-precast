from odoo import api,fields,models,_ 

class AdhPreMasterPlant(models.Model):
	_name = 'adhimix.pre.master.plant'

	name = fields.Char("Nama Plant")
	company_ids = fields.Many2many(comodel_name='res.company',string='Plant')


class ResCompany(models.Model):
	_inherit = 'res.company'

	kode_company = fields.Char("Kode Organisasi")
	jenis_produk = fields.Selection([('Infrastucture','Infrastucture'),('Gedung','Gedung')
									,('Understructure','Understructure'),('Beton','Beton')],string="Jenis Produk")

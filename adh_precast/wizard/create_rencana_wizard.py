from odoo import api,fields,models,_ 
from datetime import datetime, timedelta
from odoo.exceptions import except_orm, Warning, RedirectWarning

class AdhimixCreateRencanaProduksiWizard(models.Model):
	_name = 'adhimix.create.rencana.produksi.wizard'

	product_id = fields.Many2one('product.product','Produk')
	date_from = fields.Date("Date Form")
	date_to = fields.Date("Date To")
	volume = fields.Float("Volume")
	rencana_id = fields.Many2one('adhimix.pre.rencana.produksi','Rencana')
	line_id = fields.Many2one('adhimix.pre.line', 'Line Produksi')
	nama_proyek_id = fields.Many2one('project.project','Nama Proyek')
	company_id = fields.Many2one('res.company','Plant')

	@api.multi
	def create_buat_rencana(self):
		rencana_produksi_obj = self.env['adhimix.pre.rencana.produksi']
		rencana_produksi_line_obj = self.env['adhimix.pre.rencana.produksi.plan']

		df = datetime.strptime(self.date_from, '%Y-%m-%d')
		dt = datetime.strptime(self.date_to, '%Y-%m-%d')
		total_rencana = ((dt-df).days + 1) * self.volume
		if total_rencana > self.rencana_id.sisa_rap:
			raise Warning('Total Rencana Tidak Boleh Melebihi Sisa RAP !!!')
		delta = timedelta(days=1)
		while (df <= dt):
			rencana_produksi_line_id = rencana_produksi_line_obj.create({
					'reference'		: self.rencana_id.id,
					'date'			: df,
					'product_id'	: self.product_id.id,
					'volume'		: self.volume,
					'nama_proyek_id': self.nama_proyek_id.id,
					'company_id'	: self.company_id.id,
					'jenis_produk' 	: self.product_id.jenis_produk,
					'line_id'		: self.line_id.id
					})
			df += delta
		self.rencana_id.write({
			'total_rencana': total_rencana

			})
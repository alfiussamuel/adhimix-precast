from odoo import api,fields,models,_
import time
from odoo.exceptions import except_orm, Warning, RedirectWarning
	
class AdhimixPreRencanaProduksi(models.Model):
	_name = "adhimix.pre.rencana.produksi"

	name = fields.Char('No',readonly=True)
	company_id = fields.Many2one('res.company', 'Organisasi')
	cost_control_id = fields.Many2one('adhimix.pre.cost.control', 'No Cost Control')
	nama_proyek_id = fields.Many2one('project.project','Nama Proyek')
	company_id = fields.Many2one('res.company','Plant')
	kapasitas_produksi = fields.Float("Kapasitas Produksi",compute="_get_kapasitas_produksi")
	product_id = fields.Many2one('product.product', 'Nama Produk',compute="_get_product")
	line_id = fields.Many2one('adhimix.pre.line', 'Line Produksi')
	sisa_rap = fields.Float('Sisa RAP',compute="_get_sisa_rap")
	total_rencana = fields.Float("Total Rencana",copy= False,compute="_get_total_rencana")
	plan_list_ids = fields.One2many('adhimix.pre.rencana.produksi.plan','reference')	


	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('adhimix.pre.rencana.produksi')		
		return super(AdhimixPreRencanaProduksi, self).create(vals)



	def unlink(self):
		for res in self:
			active_mo = self.env['adhimix.pre.rencana.produksi.plan'].search([('reference','=',res.id)])
			if active_mo:
				active_mo.unlink()

	# Domain Proyek Dan Cost Control
	@api.onchange('company_id','nama_proyek_id','cost_control_id')
	def onchange_jenis_komposit(self):
		ids_project = []
		ids_cost_control = []
		domain = {}
		project_lines = self.env['project.project'].search([
			('company_id','=',self.company_id.id)
			])
		cost_lines = self.env['adhimix.pre.cost.control'].search([
			('nama_proyek_id','=',self.nama_proyek_id.id)
			])
		for po_line in project_lines :
			ids_project.append(po_line.id)

		for cost_id in cost_lines :
			ids_cost_control.append(cost_id.id)

		domain = {'nama_proyek_id': [('id', 'in', ids_project)],'cost_control_id' : [('id', '=', ids_cost_control)]} 
		return {'domain':domain}
	@api.multi
	def button_buat_rencana(self, vals):
		for res in self:
			ir_model_data = self.env['ir.model.data']
			compose_form_id = ir_model_data.get_object_reference('adh_precast', 'create_rencana_produksi_wizard')[1]
			
			return {
	            'type': 'ir.actions.act_window',
	            'view_type': 'form',
	            'view_mode': 'form',
	            'res_model': 'adhimix.create.rencana.produksi.wizard',
	            'views': [(compose_form_id, 'form')],
	            'view_id': compose_form_id,
	            'target': 'new',
	            'context': {
		                'default_product_id' : res.product_id.id,
		                'default_rencana_id' : res.id,
		                'default_company_id' : res.company_id.id,
		                'default_nama_proyek_id' : res.nama_proyek_id.id,
		                'default_line_id'	: res.line_id.id,

		            }
			    }

	

	@api.one
	@api.depends('plan_list_ids.volume')
	def _get_total_rencana(self):
		for rec in self:
			for res in self.plan_list_ids:
				rec.total_rencana += res.volume
				if rec.total_rencana > rec.sisa_rap:
					raise Warning('Total Rencana Tidak Boleh Melebihi Sisa RAP !!!')

	@api.one
	@api.depends('line_id')
	def _get_kapasitas_produksi(self):
		for res in self.line_id:
			self.kapasitas_produksi = res.kapasitas_line

	@api.one
	@api.depends('cost_control_id')
	def _get_product(self):
		for res in self.cost_control_id:
			self.product_id = res.product_id.id

	@api.one
	@api.depends('cost_control_id')
	def _get_sisa_rap(self):
		for res in self.cost_control_id:
			self.sisa_rap = res.sisa_rap




class AdhimixPreRencanaProduksiPlan(models.Model):
	_name = "adhimix.pre.rencana.produksi.plan"
	
	reference = fields.Many2one(comodel_name='adhimix.pre.rencana.produksi', string='Reference')
	date = fields.Date('Tanggal')
	product_id = fields.Many2one('product.product', 'Nama Produk')
	volume = fields.Float('Volume')
	nama_proyek_id = fields.Many2one('project.project','Nama Proyek')
	line_id = fields.Many2one('adhimix.pre.line', 'Line Produksi')
	company_id = fields.Many2one('res.company','Plant')
	jenis_produk = fields.Selection([('Infrastucture','Infrastucture'),('Gedung','Gedung')
									,('Understructure','Understructure'),('Beton','Beton')],string="Jenis Produk")
	
	


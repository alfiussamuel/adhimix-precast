from odoo import api,fields,models,_ 

class ProjectProjectt(models.Model):
	_inherit = 'project.project'

	company_id = fields.Many2many(comodel_name='res.company',string='Plant')




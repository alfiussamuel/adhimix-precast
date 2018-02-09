from odoo import api,fields,models,_ 

class AdhimixCreateBuatRencanaWizard(models.Model):
	_name = 'adhimix.create.buat.rencana.wizard'

	date_from = fields.Date("Date Form")
	date_to = fields.Date("Date To")
	volume = fields.Float("Volume")
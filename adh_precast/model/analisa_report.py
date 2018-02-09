from odoo import api,fields,models,_ 

class report_analisa_pasar(models.Model):
	_name = 'report.adh_mrp_pemasaran.report_analisa_pasar'


	@api.model
	def get_analisa_pasar_details(self,keputusan_akhir=False):
		analisa_pasar_ids = self.env['adhimix.mrp.info.pasar.line'].search([
			('keputusan_akhir','=',keputusan_akhir)
			])

		for analisa_id in analisa_pasar_ids:
			product_analisa = analisa_id.product_id._name
			company_id = analisa_id.reference.company_id.logo
			nomor_dokumen = analisa_id.reference.name
			tanggal_efektif	=analisa_id.reference.tanggal_efektif
			nama_pelanggan = analisa_id.reference.nama_pelanggan.name
			nama_spesifikasi = analisa_id.nama_spesifikasi_produk
			spesifikasi_bahan	= analisa_id.Spesifikasi_bahan_hal2_khusus
			desain_produk		= analisa_id.desain_produk_hal2_khusus
			analisa_hal2		= analisa_id.analisa_hal2_khusus
			keputusan_akhir_hal2 =analisa_id.keputusan_hal2_khusus
			kapasitas_produksi	= analisa_id.kapasitas_produksi
			sisa_kapasitas		= analisa_id.sisa_kapasitas
			analisa_perbandingan = analisa_id.analisa_perbandingan_waktu
			keputusan_akhir_perbandingan	= analisa_id.keputusan_perbandingan_waktu
			status			= analisa_id.status_pembayaran
			analisa_status	= analisa_id.analisa_status_pembayaran
			keputusan_status = analisa_id.keputusan_status
			keputusan_akhir  = analisa_id.keputusan_akhir

		return{
			'analisa_pasar_ids' : analisa_pasar_ids,
			'product_analisa'	: product_analisa,
			'company_id'		: company_id,
			'nomor_dokumen'		: nomor_dokumen,
			'tanggal_efektif'	: tanggal_efektif,
			'nama_pelanggan'	: nama_pelanggan,
			'nama_spesifikasi'	: nama_spesifikasi,
			'spesifikasi_bahan'	: spesifikasi_bahan,
			'desain_produk'		: desain_produk,
			'analisa_hal2'		: analisa_hal2,
			'keputusan_akhir_hal2': keputusan_akhir_hal2,
			'kapasitas_produksi'	: kapasitas_produksi,
			'sisa_kapasitas'	: sisa_kapasitas,
			'analisa_perbandingan' : analisa_perbandingan,
			'keputusan_akhir_perbandingan' : keputusan_akhir_perbandingan,
			'status'				: status,
			'analisa_status'		:analisa_status,
			'keputusan_status'		:keputusan_status,
			'keputusan_akhir'		:keputusan_akhir

		}

	@api.multi
	def render_html(self, docids, data=None):
		data = dict(data or {})        
		# data.update(self.get_evaluasi_penawaran_details(data['tanggal_penawaran']))
		data.update(self.get_analisa_pasar_details(data['keputusan_akhir']))
		return self.env['report'].render('adh_mrp_pemasaran.report_analisa_pasar', data)

from odoo import api,fields,models,_

class ReportInfoPasar(models.AbstractModel):

    _name = 'report.adh_precast.report_infopasar'

    @api.model
    # def get_info_pasar_details(self, tanggal_informasi=False):
    def get_info_pasar_details(self, date_start =False,date_stop=False):

        if date_start:
            date_start = fields.Datetime.from_string(date_start)
        else:
            # start by default today 00:00:00
            date_start = today

        if date_stop:
            # set time to 23:59:59
            date_stop = fields.Datetime.from_string(date_stop)
        else:
            # stop by default today 23:59:59
            date_stop = today + timedelta(days=1, seconds=-1)

        # avoid a date_stop smaller than date_start
        date_stop = max(date_stop, date_start)

        date_start = fields.Datetime.to_string(date_start)
        date_stop = fields.Datetime.to_string(date_stop)

        info_pasar_ids = self.env['adhimix.pre.info.pasar'].search([
        	# ('tanggal_informasi','<=',tanggal_informasi)
            ('tanggal_informasi','>=',date_start),
            ('tanggal_informasi','<=',date_stop)
        	])
                
        for info_pasar in info_pasar_ids:
        	nomor_info = info_pasar.name 
                company_id = info_pasar.company_id.logo
                tanggal_efektif = info_pasar.tanggal_efektif 
                tanggal_informasi = info_pasar.tanggal_informasi
                # nama_pelanggan = info_pasar.nama_pelanggan.name 
                # nama_spesifikasi_produk = info_pasar.nama_spesifikasi_produk
                # volume = info_pasar.volume
                tanggal_dibutuhkan = info_pasar.tanggal_dibutuhkan
                lokasi = info_pasar.lokasi
                sumber_informasi_dari = info_pasar.sumber_informasi_dari
                sumber_informasi_cara = info_pasar.sumber_informasi_cara
                nama_contact_person = info_pasar.nama
                telepon = info_pasar.telepon
                status = info_pasar.status
                ya = info_pasar.ya
                tidak = info_pasar.tidak


        return {
            'info_pasar_ids':info_pasar_ids,
            'nomor_info': nomor_info,
            'company_id' : company_id,
            'tanggal_efektif' : tanggal_efektif,
            # 'tanggal_informasi' : tanggal_informasi,
            # 'nama_pelanggan' : nama_pelanggan,
            # 'nama_spesifikasi_produk': nama_spesifikasi_produk,
            # 'volume' : volume ,
            # 'tanggal_dibutuhkan':tanggal_dibutuhkan,
            # 'lokasi' : lokasi,
            # 'sumber_informasi_dari' : sumber_informasi_dari,
            # 'sumber_informasi_cara' : sumber_informasi_cara,
            # 'nama_contact_person' : nama_contact_person,
            # 'telepon' : telepon,
            # 'status' : status,
            # 'ya' : ya,
            # 'tidak':tidak
                # })
                # for (info_pasar_ids, company_id) qty in products_sold.items()], key=lambda l: l['product_name'])
            } 

    @api.multi
    def render_html(self, docids, data=None):
        data = dict(data or {})        
        # data.update(self.get_info_pasar_details(data['tanggal_informasi']))
        data.update(self.get_info_pasar_details(data['date_start'],data['date_stop']))
        return self.env['report'].render('adh_precast.report_infopasar', data)

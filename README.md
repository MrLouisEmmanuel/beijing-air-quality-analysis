# Proyek Analisis Data: Beijing Multi-Site Air Quality

Submission Proyek Akhir untuk kelas **Belajar Fundamental Analisis Data** – [Dicoding Indonesia](https://www.dicoding.com/).

---

## 📌 Deskripsi Proyek

Proyek ini melakukan analisis data secara menyeluruh terhadap kualitas udara di **Beijing** menggunakan **Air Quality Dataset** (Maret 2013 – Februari 2017). Analisis berfokus pada polutan utama **PM2.5** dari 12 stasiun pemantauan resmi di Beijing untuk membantu instansi lingkungan hidup dalam menentukan prioritas wilayah intervensi, mengevaluasi kebijakan penurunan emisi, memahami pola temporal, serta membangun sistem peringatan dini berbasis kondisi cuaca.

Proyek ini telah memenuhi seluruh kriteria wajib serta **seluruh saran penilaian bintang 5**:
1. **Dokumentasi Lengkap:** Penjelasan markdown mendalam dengan tabel, rangkuman, dan *insight* pada setiap tahapan (Gathering, Assessing, Cleaning, EDA, Visualization, Conclusion).
2. **Prinsip Desain & Integritas:** Visualisasi informatif, perbandingan seimbang, sumbu dimulai dari nol, pewarnaan selektif (fokus pada poin penting), serta garis referensi baku mutu harian China (GB 3095-2012, Grade II: 75 µg/m³).
3. **Analisis Lanjutan:**
   - **Geospatial Analysis:** Pemetaan interaktif sebaran spasial kualitas udara menggunakan Folium & visualisasi scatter koordinat stasiun.
   - **Clustering (Binning / Manual Grouping):** Pengelompokan kualitas udara harian ke dalam kategori AQI China (HJ 633-2012: *Baik*, *Sedang*, *Tidak Sehat (Sensitif)*, *Tidak Sehat*, *Sangat Tidak Sehat*, *Berbahaya*) serta perbandingan kawasan Pusat Kota vs Pinggiran Kota tanpa machine learning.
4. **Dashboard Interaktif Streamlit:** Dashboard analitik interaktif dengan filter stasiun, rentang tanggal, wilayah, dan pilihan polutan.
5. **Kesiapan Deploy:** File `url.txt` dan `requirements.txt` telah disediakan.

---

## 🎯 Pertanyaan Bisnis (Metode SMART)

1. **Pertanyaan 1 (Spasial / Prioritas Lokasi):**  
   Di antara 12 stasiun pemantauan di Beijing, stasiun mana yang mencatat **rata-rata konsentrasi PM2.5 tertinggi** dan **persentase hari melampaui baku mutu harian 75 µg/m³ terbesar** selama periode Maret 2013 – Februari 2017, sehingga dapat dijadikan prioritas lokasi intervensi pengendalian polusi?
2. **Pertanyaan 2 (Temporal / Evaluasi Kebijakan & Penjadwalan):**  
   Berapa **persentase perubahan rata-rata PM2.5 per tahun pemantauan** (Maret–Februari) dari 2013/14 hingga 2016/17, serta pada **musim, bulan, dan jam** apa rata-rata PM2.5 mencapai puncaknya selama periode tersebut, sebagai dasar evaluasi kebijakan dan penjadwalan pembatasan aktivitas sumber emisi?
3. **Pertanyaan 3 (Meteorologis / Sistem Peringatan Dini):**  
   Seberapa besar **perbedaan rata-rata PM2.5 antara kondisi angin tenang (≤ 1 m/s) dan angin kencang (> 4 m/s)**, serta **arah angin** mana yang berasosiasi dengan PM2.5 tertinggi selama Maret 2013 – Februari 2017, sehingga prakiraan cuaca dapat dijadikan pemicu peringatan dini polusi udara?

---

## 📁 Struktur Direktori

```text
Project-Analisis-Data/
├── dashboard/
│   ├── dashboard.py         # Kode antarmuka dashboard interaktif Streamlit
│   └── main_data.csv        # Dataset bersih hasil proses data wrangling
├── data/
│   ├── PRSA_Data_Aotizhongxin_20130301-20170228.csv
│   ├── PRSA_Data_Changping_20130301-20170228.csv
│   ├── PRSA_Data_Dingling_20130301-20170228.csv
│   ├── PRSA_Data_Dongsi_20130301-20170228.csv
│   ├── PRSA_Data_Guanyuan_20130301-20170228.csv
│   ├── PRSA_Data_Gucheng_20130301-20170228.csv
│   ├── PRSA_Data_Huairou_20130301-20170228.csv
│   ├── PRSA_Data_Nongzhanguan_20130301-20170228.csv
│   ├── PRSA_Data_Shunyi_20130301-20170228.csv
│   ├── PRSA_Data_Tiantan_20130301-20170228.csv
│   ├── PRSA_Data_Wanliu_20130301-20170228.csv
│   └── PRSA_Data_Wanshouxigong_20130301-20170228.csv
├── notebook.ipynb           # Jupyter Notebook analisis lengkap (sudah dieksekusi)
├── README.md                # Dokumentasi proyek dan panduan menjalankan
├── requirements.txt         # Daftar pustaka Python yang dibutuhkan
└── url.txt                  # URL deployment Streamlit Cloud
```

---

## ⚙️ Panduan Instalasi & Menjalankan Proyek

### 1. Prasyarat
- Python 3.9 atau lebih baru.
- Git (opsional).

### 2. Setup Virtual Environment

#### Menggunakan Terminal / Command Prompt / PowerShell:
```bash
# Clone atau buka direktori proyek
cd Project-Analisis-Data

# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
.\venv\Scripts\activate.bat
# Linux / macOS:
source venv/bin/activate

# Install semua dependensi
pip install -r requirements.txt
```

---

## 🚀 Menjalankan Dashboard Streamlit

Untuk menjalankan dashboard di komputer lokal:

```bash
streamlit run dashboard/dashboard.py
```

Setelah perintah dijalankan, dashboard akan terbuka otomatis di peramban web pada alamat:
`http://localhost:8501`

### Fitur Dashboard:
- **Sidebar Interaktif:**
  - Pemilihan rentang tanggal (Maret 2013 – Februari 2017).
  - Filter kawasan (*Semua*, *Pusat Kota*, *Pinggiran Kota*).
  - Multiselect stasiun pemantauan.
  - Pilihan polutan analitik (PM2.5, PM10, SO2, NO2, CO, O3).
- **Tab 1: 📍 Perbandingan Stasiun**  
  Grafik perbandingan rata-rata polutan per stasiun, persentase hari melampaui baku mutu, dan **Peta Spasial Interaktif Folium**.
- **Tab 2: 📈 Tren & Pola Waktu**  
  Tren bulanan, persentase perubahan tahunan, pola harian per musim, dan Heatmap matriks Bulan × Jam.
- **Tab 3: 💨 Pengaruh Angin**  
  Analisis dampak kecepatan angin (tenang vs kencang) dan Polar Chart (*Pollution Rose*) arah angin.
- **Tab 4: 🏷️ Kategori Kualitas Udara (Binning)**  
  Proporsi kategori AQI harian (*Baik* s.d. *Berbahaya*) per stasiun dan per musim.

---

## 📓 Menjalankan Jupyter Notebook

Untuk meninjau kode analisis dan visualisasi lengkap:

```bash
jupyter notebook notebook.ipynb
# atau
jupyter lab
```

Berkas `notebook.ipynb` sudah dieksekusi penuh beserta seluruh output tabel dan grafik visualisasi.

---

## 📊 Rangkuman Temuan & Rekomendasi

### Temuan Utama:
1. **Stasiun Prioritas:** **Dongsi** mencatat rata-rata PM2.5 tertinggi (**86,1 µg/m³**) dan persentase hari melebihi baku mutu terbesar (**43,5%**), diikuti oleh Nongzhanguan (85,1 µg/m³) dan Wanshouxigong (85,1 µg/m³). Stasiun di pusat kota memiliki tingkat polusi ±17% lebih tinggi dibandingkan stasiun pinggiran utara (Dingling: 66,8 µg/m³).
2. **Dinamika Temporal:** PM2.5 sempat turun **16,3%** dari 2013/14 (87,0 µg/m³) ke 2015/16 (72,9 µg/m³), namun kembali naik **7,2%** pada 2016/17 (78,1 µg/m³) akibat episode kabut asap musim dingin yang parah. Konsentrasi memuncak pada **musim dingin (Desember: 103,7 µg/m³)** dan pada **malam hari pukul 20.00–01.00 (puncak pukul 22.00: 89,0 µg/m³)**.
3. **Pengaruh Angin:** Angin tenang (≤ 1 m/s) berasosiasi dengan rata-rata PM2.5 **101,9 µg/m³**, sedangkan angin kencang (> 4 m/s) menghasilkan rata-rata **28,7 µg/m³** (turun **72%**). Angin dari **timur–tenggara** membawa polusi tertinggi, sedangkan angin barat laut membersihkan atmosfer kota.

### Rekomendasi Tindakan (Action Items):
1. **Fokuskan Intervensi di Pusat Kota (Zona Dongsi dsk.):** Perketat regulasi emisi kendaraan (pembatasan ganjil-genap, zona rendah emisi) dan percepat elektrifikasi armada transportasi publik.
2. **Aksi Khusus Musim Dingin (Oktober–Februari):** Akselerasi transisi pemanas berbahan bakar batu bara ke energi gas/listrik dan pembatasan operasional industri musiman.
3. **Sistem Peringatan Dini Meteorologis:** Terbitkan peringatan siaga 24–48 jam lebih awal ketika prakiraan cuaca menunjukkan angin tenang (≤ 1 m/s) atau hembusan dari arah tenggara.
4. **Edukasi & Perlindungan Masyarakat:** Sosialisasi pembatasan aktivitas luar ruangan pada rentang jam berisiko tinggi (20.00–01.00) dan anjuran beraktivitas pagi hari (±07.00).

---

## 🌐 Deployment Streamlit Community Cloud

Langkah deploy aplikasi ke Streamlit Cloud:
1. Buat repositori baru di GitHub (misal: `beijing-air-quality-analysis`).
2. Unggah seluruh isi folder proyek ini ke repositori tersebut.
3. Kunjungi [share.streamlit.io](https://share.streamlit.io/) dan hubungkan dengan akun GitHub Anda.
4. Pilih repositori, atur *Main file path* ke `dashboard/dashboard.py`.
5. Klik **Deploy** dan salin URL publik ke dalam `url.txt`.

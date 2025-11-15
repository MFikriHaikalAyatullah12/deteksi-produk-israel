# Deteksi Produk Israel - AI Detection System

Sistem deteksi produk terafiliasi Israel menggunakan teknologi AI Random Forest dengan antarmuka web berbasis Next.js.

## 📋 Fitur Utama

- **Deteksi Real-time**: Menggunakan kamera laptop atau handphone (via USB)
- **Upload Gambar**: Analisis gambar produk yang di-upload
- **AI Random Forest**: Model machine learning untuk deteksi akurat
- **Dashboard Interaktif**: Antarmuka web yang user-friendly
- **Riwayat Deteksi**: Menyimpan hasil deteksi sebelumnya
- **Database Lengkap**: Berisi informasi brand dan produk terafiliasi Israel

## 🎯 Kriteria Deteksi

Sistem mendeteksi produk berdasarkan:

### Identitas Fisik
- ✅ Barcode dengan prefix 729 (kode negara Israel)
- ✅ Label "Made in Israel" atau "Product of Israel"
- ✅ Tulisan bahasa Ibrani
- ✅ Sertifikasi kosher Israel (Badatz, OU Kosher, Kof-K, Star-K)
- ✅ Logo perusahaan Israel

### Brand Terafiliasi
- **Unilever**: Dove, Rexona, Lux, Vaseline, Ponds, Lifebuoy, Clear, Sunsilk, dll.
- **Nestlé**: Nescafé, Milo, KitKat, Maggi, Dancow, Nestum, dll.
- **P&G**: Pampers, Pantene, Head & Shoulders, Rejoice, Oral-B, Gillette, dll.
- **Coca-Cola**: Coca-Cola, Sprite, Fanta, Minute Maid, Aquarius, Ades
- **PepsiCo**: Pepsi, Lays, Cheetos, Quaker, Gatorade, Tropicana
- **L'Oréal**: L'Oréal Paris, Garnier, Maybelline, NYX, Vichy, dll.
- **Dan banyak lagi...**

## 🛠️ Teknologi Yang Digunakan

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React Webcam** - Camera integration
- **Lucide React** - Icons

### Backend
- **FastAPI** - Python web framework
- **scikit-learn** - Random Forest model
- **OpenCV** - Image processing
- **EasyOCR** - Text recognition
- **pyzbar** - Barcode detection

### AI/ML
- **Random Forest Classifier** - Primary detection model
- **Computer Vision** - Image analysis
- **OCR (Optical Character Recognition)** - Text extraction
- **Feature Engineering** - Multi-modal feature extraction

## 🚀 Quick Start

```bash
# 1. Install dependencies
npm install
cd backend && pip install -r requirements.txt

# 2. Start backend
cd backend && python main.py

# 3. Start frontend (new terminal)  
npm run dev

# 4. Open browser: http://localhost:3000
```

## 📱 Cara Penggunaan

### 1. Deteksi via Kamera
1. Klik tombol "Buka Kamera"
2. Arahkan kamera ke produk yang ingin dideteksi
3. Klik "Ambil Foto" untuk memulai analisis
4. Tunggu hasil deteksi muncul di panel kanan

### 2. Upload Gambar
1. Klik tombol "Upload Gambar" 
2. Pilih file gambar produk (JPG, PNG, dll.)
3. Gambar akan otomatis dianalisis
4. Lihat hasil di panel hasil deteksi

### 3. Membaca Hasil
- **Hijau**: Produk aman (bukan afiliasi Israel)
- **Merah/Orange**: Produk terafiliasi Israel
- **Confidence Level**: Tingkat keyakinan AI (0-100%)
- **Detected Features**: Fitur yang terdeteksi pada produk
- **Brand Info**: Informasi detail brand (jika terdeteksi)
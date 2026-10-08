# Elit Barber - Online Randevu Sistemi

Profesyonel erkek kuaförü için geliştirilmiş modern, mobil uyumlu online randevu alma uygulaması.

**Teknolojiler:** Flask • SQLite • HTML/CSS/JavaScript

---

## Özellikler

### Müşteri Tarafı
- Hizmet, usta, tarih ve saat seçerek kolay randevu alma
- Gerçek zamanlı müsait saat kontrolü (çakışma engelleme)
- Geçmiş saatlere randevu alınamaz
- Cihaz bazlı limit: Son 24 saatte en fazla **3 randevu**
- Galeri + Hakkımızda sayfası
- Mobil uyumlu modern arayüz

### Admin Paneli
- Randevu yönetimi (Yaklaşan / Geçmiş)
- Toplu silme (Yaklaşan, Geçmiş, Tümü)
- Hizmet ekleme / güncelleme / silme (süre + fiyat)
- Usta ekleme / silme
- Galeri resmi yükleme (4 adet .jpg)

---

## Kurulum

### 1. Gereksinimler
- Python 3.8+
- pip

### 2. Bağımlılıkları Yükle
```bash
pip install flask

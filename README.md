# 💈 Elit Barber — Online Randevu Sistemi

> Modern, hızlı ve mobil uyumlu bir **erkek kuaförü / berber randevu yönetim sistemi**.

**Elit Barber**, müşterilerin internet üzerinden istedikleri hizmeti, ustayı, tarihi ve uygun saati seçerek kolayca randevu oluşturmasını; işletme sahibinin ise tüm randevuları ve salon içerisindeki hizmet/usta bilgilerini merkezi bir yönetim panelinden kontrol etmesini sağlayan web tabanlı bir uygulamadır.

---

## ✨ Öne Çıkan Özellikler

### 👤 Müşteri Tarafı

- 💇 Hizmet seçerek randevu oluşturma
- 💈 İstenilen ustayı seçebilme
- 📅 Tarih ve saat seçimi
- 🕐 Gerçek zamanlı müsaitlik kontrolü
- 🚫 Dolu saatlere çakışan randevu oluşturmayı engelleme
- ⏰ Geçmiş tarih ve saatlere randevu alınmasını engelleme
- 🔒 Son 24 saat içerisinde cihaz başına en fazla **3 randevu**
- 🖼️ İşletme galerisi
- ℹ️ Hakkımızda bölümü
- 📱 Mobil cihazlarla uyumlu responsive tasarım

### 🔐 Admin Paneli

Yönetim paneli üzerinden işletmenin günlük operasyonları kolayca yönetilebilir.

- 📋 Yaklaşan randevuları görüntüleme
- 🕘 Geçmiş randevuları görüntüleme
- 🗑️ Randevu silme
- 🧹 Yaklaşan randevuları toplu silme
- 🧹 Geçmiş randevuları toplu silme
- 🧹 Tüm randevuları temizleme
- ✂️ Yeni hizmet ekleme
- ✏️ Hizmet bilgilerini güncelleme
- 🗑️ Hizmet silme
- 💰 Hizmet fiyatı ve süresini yönetme
- 💈 Usta ekleme
- 🗑️ Usta silme
- 🖼️ Galeri görsellerini yönetme

---

## 🛠️ Teknolojiler

| Teknoloji | Kullanım Alanı |
|---|---|
| 🐍 **Python** | Backend |
| 🌶️ **Flask** | Web framework |
| 🗄️ **SQLite** | Veritabanı |
| 🌐 **HTML5** | Sayfa yapısı |
| 🎨 **CSS3** | Arayüz ve responsive tasarım |
| ⚡ **JavaScript** | Dinamik kullanıcı etkileşimleri |

---

## 🏗️ Uygulama Mimarisi

Proje temel olarak üç ana katmandan oluşmaktadır:

```text
┌──────────────────────────────────────┐
│              CLIENT                  │
│       HTML / CSS / JavaScript        │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│              BACKEND                 │
│               Flask                  │
│                                      │
│  • Randevu işlemleri                 │
│  • Müsaitlik kontrolü                │
│  • Admin işlemleri                   │
│  • Hizmet / Usta yönetimi            │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│             DATABASE                 │
│               SQLite                 │
│                                      │
│  • Randevular                        │
│  • Hizmetler                         │
│  • Ustalar                           │
└──────────────────────────────────────┘
```

---

## 📁 Proje Yapısı

Projenin ana uygulaması `barber-booking` klasörü altında bulunmaktadır.

Genel yapı:

```text
Barber-Booking/
│
├── barber-booking/
│   ├── ...
│   └── ...
│
├── LICENSE
└── README.md
```

> Uygulamanın backend, frontend, template, static dosyaları ve veritabanı bileşenleri `barber-booking` klasörü içerisinde yer almaktadır.

---

## 🚀 Kurulum

### 1. Repository'yi klonlayın

```bash
git clone https://github.com/Asu-developer/Barber-Booking.git
```

Proje klasörüne girin:

```bash
cd Barber-Booking
```

Ardından uygulamanın bulunduğu klasöre geçin:

```bash
cd barber-booking
```

---

### 2. Python sürümünü kontrol edin

Projenin mevcut README'sine göre **Python 3.8+** gereklidir.

```bash
python --version
```

veya:

```bash
python3 --version
```

---

### 3. Flask'ı yükleyin

```bash
pip install flask
```

Daha izole bir geliştirme ortamı için virtual environment kullanmanız önerilir:

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux / macOS:

```bash
source venv/bin/activate
```

Ardından:

```bash
pip install flask
```

---

## ▶️ Uygulamayı Çalıştırma

Uygulamanın Flask giriş dosyasından çalıştırılması gerekir.

Örneğin giriş dosyanız `app.py` ise:

```bash
python app.py
```

Flask geliştirme sunucusu başladıktan sonra terminalde gösterilen local adrese tarayıcınızdan erişebilirsiniz.

Genellikle:

```text
http://127.0.0.1:5000
```

---

## 📅 Randevu Akışı

Müşteri tarafındaki temel kullanım akışı:

```text
Hizmet Seç
    ↓
Usta Seç
    ↓
Tarih Seç
    ↓
Müsait Saatleri Gör
    ↓
Saat Seç
    ↓
Randevuyu Oluştur
    ↓
Randevu Sisteme Kaydedilir
```

Sistem, mevcut randevuları kontrol ederek aynı zaman diliminde çakışan yeni bir randevunun oluşturulmasını engeller.

Ayrıca geçmiş tarih/saatlere randevu oluşturulamaz.

---

## 🛡️ Randevu Kuralları

Uygulamadaki randevu sistemi bazı temel kurallara sahiptir:

- Geçmiş saatlere randevu alınamaz.
- Aynı zaman dilimine çakışan randevular engellenir.
- Bir cihaz üzerinden son 24 saat içerisinde en fazla **3 randevu** oluşturulabilir.
- Müsait olmayan saatler kullanıcıya uygun seçenek olarak sunulmaz.

Bu kurallar, işletmenin randevu trafiğini daha düzenli yönetmesine yardımcı olur.

---

## 🎨 Admin Paneli

Admin paneli işletme sahibinin günlük operasyonlarını yönetebilmesi için tasarlanmıştır.

### Randevu Yönetimi

```text
Yaklaşan Randevular
        │
        ├── Görüntüle
        └── Sil

Geçmiş Randevular
        │
        ├── Görüntüle
        └── Sil
```

Ayrıca toplu silme seçenekleri ile:

- Yaklaşan randevular
- Geçmiş randevular
- Tüm randevular

yönetilebilir.

### Hizmet Yönetimi

Admin tarafından hizmetler için:

- Hizmet adı
- Süre
- Fiyat

gibi bilgiler yönetilebilir.

### Usta Yönetimi

Salon içerisinde çalışan ustalar sisteme eklenebilir veya mevcut ustalar kaldırılabilir.

---

## 📱 Responsive Tasarım

Elit Barber, masaüstü bilgisayarların yanı sıra mobil cihazlarda da kullanılabilecek şekilde tasarlanmıştır.

```text
Desktop        Tablet        Mobile
┌─────────┐    ┌───────┐     ┌─────┐
│         │    │       │     │     │
│  WEB    │    │  WEB  │     │ WEB │
│         │    │       │     │     │
└─────────┘    └───────┘     └─────┘
```

Bu sayede müşteriler telefonlarından da randevu oluşturabilir.

---

## 🖼️ Galeri

Uygulamada işletmenin görsellerini göstermek için bir galeri bölümü bulunmaktadır.

Admin paneli üzerinden galeri görsellerinin yönetilmesi desteklenmektedir.

---

## 🔒 Güvenlik ve İş Kuralları

Uygulamanın randevu sisteminde özellikle aşağıdaki durumlar kontrol edilir:

- ❌ Geçmiş zamanlı randevu
- ❌ Aynı saat için çakışan randevu
- ❌ Belirlenen günlük cihaz limitinin aşılması

Bu kontroller, basit bir randevu formunun ötesinde daha kontrollü bir booking deneyimi oluşturur.

---

## 💡 Kullanım Alanları

Bu proje özellikle:

- 💈 Berberler
- ✂️ Erkek kuaförleri
- 💇 Kuaför salonları
- 🧔 Barber shop'lar
- 🏪 Küçük işletmeler

için temel bir online randevu altyapısı olarak kullanılabilir.

---

## 🔮 Gelecekte Eklenebilecek Özellikler

Projeyi daha ileri seviyeye taşımak için aşağıdaki özellikler eklenebilir:

- [ ] Kullanıcı hesabı ve üyelik sistemi
- [ ] SMS / WhatsApp randevu bildirimi
- [ ] E-posta bildirimleri
- [ ] Randevu iptal etme
- [ ] Randevu değiştirme
- [ ] Usta bazlı çalışma saatleri
- [ ] Usta bazlı müsaitlik takvimi
- [ ] Online ödeme
- [ ] Dashboard istatistikleri
- [ ] Günlük / haftalık / aylık gelir raporları
- [ ] Müşteri geçmişi
- [ ] Değerlendirme ve yorum sistemi
- [ ] Çoklu işletme desteği
- [ ] REST API
- [ ] Docker desteği
- [ ] Production deployment
- [ ] Otomatik testler

---

## 🧪 Geliştirme

Projeye katkıda bulunmak veya kendi ihtiyaçlarınıza göre geliştirmek için repository'yi fork edebilir ve yeni bir branch oluşturabilirsiniz.

```bash
git checkout -b feature/new-feature
```

Değişikliklerinizi yaptıktan sonra:

```bash
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature
```

Ardından GitHub üzerinden Pull Request oluşturabilirsiniz.

---

## 📄 Lisans

Bu proje **MIT License** altında yayınlanmıştır.

Detaylar için [`LICENSE`](./LICENSE) dosyasına bakabilirsiniz.

---

## 👨‍💻 Geliştirici

**Asu-developer**

GitHub:  
https://github.com/Asu-developer

---

<div align="center">

### 💈 Elit Barber

**Online randevu yönetimini kolaylaştırın.**

⭐ Projeyi beğendiyseniz repository'ye star bırakabilirsiniz.

</div>

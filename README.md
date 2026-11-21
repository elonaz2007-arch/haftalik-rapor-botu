# Haftalık Faaliyet Raporu Botu (Weekly Activity Report Bot)

Günlük alınan kısa aktivite notlarını **Google Gemini AI** kullanarak resmi ve kurumsal bir dile dönüştüren, otomatik olarak biçimlendirilmiş Word (`.docx`) raporu oluşturan ve **Google Drive**'a yedekleyen Python tabanlı Telegram botu.

## Özellikler
- **Yapay Zeka Destekli Metin Düzenleme:** Ham notları Gemini API ile akıcı ve profesyonel rapor maddelerine çevirir.
- **Otomatik Word (.docx) Çıktısı:** `python-docx` kütüphanesi ile standart formatta haftalık rapor belgesi üretir.
- **Google Drive Arşivleme:** Oluşturulan raporları belirlenen Google Drive klasörüne otomatik olarak yükler.

## Kurulum ve Çalıştırma

### 1. Depoyu Bilgisayarınıza İndirin
```bash
git clone [https://github.com/elonaz2007-arch/haftalik-rapor-botu.git](https://github.com/elonaz2007-arch/haftalik-rapor-botu.git)
cd haftalik-rapor-botu

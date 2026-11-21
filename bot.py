import os
from dotenv import load_dotenv
from drive_uploader import upload_docx_to_drive
import time
import asyncio
from datetime import datetime
import json
import logging
from docx import Document
from google import genai
from google.genai import types
from pydantic import BaseModel
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

load_dotenv()

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini istemcisini başlatıyoruz
gemini_client = genai.Client(api_key=GEMINI_API_KEY)


# Yapay zekanın 5 bölümü düzenli JSON formatında döndürmesi için şema
class RaporBolumleri(BaseModel):
  projeler: str
  tamamlanan: str
  devam_eden: str
  sorunlar: str
  gelecek_plan: str


PROJELER, TAMAMLANAN, DEVAM_EDEN, SORUNLAR, GELECEK_PLAN, PUAN = range(6)


def raporu_profesyonellestir(ham_veriler: dict) -> dict:
  prompt = f"""
    Aşağıda bir çalışanın haftalık faaliyet raporu için yazdığı kısa notlar yer almaktadır.
    Bu notları anlamını bozmadan, kurumsal, resmi ve profesyonel bir haftalık rapor diliyle yeniden düzenle:

    1. Çalışılan Projeler: {ham_veriler['projeler']}
    2. Tamamlanan Görevler: {ham_veriler['tamamlanan']}
    3. Devam Eden İşler: {ham_veriler['devam_eden']}
    4. Bu Hafta Labda En Çok Zorlanılan Konu: {ham_veriler['sorunlar']}
    5. Gelecek Hafta Planları: {ham_veriler['gelecek_plan']}
    """

  ayarlar = types.GenerateContentConfig(
      response_mime_type="application/json",
      response_schema=RaporBolumleri,
      system_instruction=(
          "Sen kurumsal bir raporlama editörüsün. Kullanıcının günlük konuşma"
          " diliyle yazdığı tüm yazım, noktalama ve klavye hatalarını tamamen"
          " düzelt. Metni anlamını bozmadan akıcı, hatasız ve resmi bir iş"
          " Türkçesiyle yeniden yaz."
      ),
  )

  # Önce ana modeli dene; yoğunluk (503) varsa müsait başka bir Flash modele geç
  denenecek_modeller = ["gemini-3.8-flash"]
  try:
    for m in gemini_client.models.list():
      if (
          "flash" in m.name
          and "3.8-flash" not in m.name
          and "2.5-flash" not in m.name
      ):
        denenecek_modeller.append(m.name)
  except Exception:
    pass

  son_hata = None
  for model_adi in denenecek_modeller[:3]:
    try:
      response = gemini_client.models.generate_content(
          model=model_adi, contents=prompt, config=ayarlar
      )
      return json.loads(response.text)
    except Exception as hata:
      son_hata = hata
      logging.warning(
          f"{model_adi} yanıt vermedi ({hata}), diğer model deneniyor..."
      )

  raise son_hata


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(
      "Merhaba! Yapay zeka destekli haftalık rapor botuna hoş geldin.\n"
      "Yeni rapor oluşturmak için /yenirapor yazabilirsin.\n"
      "İşlemi yarıda bırakmak istersen /iptal yazman yeterli."
  )


async def yeni_rapor(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data.clear()
  await update.message.reply_text(
      "Haftalık rapor oluşturma başladı!\n\n"
      "1/6 - Bu hafta hangi projelerde çalıştınız?"
  )
  return PROJELER


async def projeler_al(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["projeler"] = update.message.text
  await update.message.reply_text("2/6 - Tamamlanan görevler nelerdir?")
  return TAMAMLANAN


async def tamamlanan_al(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["tamamlanan"] = update.message.text
  await update.message.reply_text("3/6 - Devam eden işler nelerdir?")
  return DEVAM_EDEN


async def devam_eden_al(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["devam_eden"] = update.message.text
  await update.message.reply_text("4/6 - Bu hafta labda en çok zorlandığın konu ne oldu?")
  return SORUNLAR


async def sorunlar_al(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["sorunlar"] = update.message.text
  await update.message.reply_text("5/6 - Gelecek hafta planları nedir?")
  return GELECEK_PLAN

async def gelecek_plan_al(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["gelecek_plan"] = update.message.text
  await update.message.reply_text(
      "6/6 - Haftayı 10 üzerinden puanla (sadece sayı yaz)."
  )
  return PUAN


async def puan_al(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["puan"] = update.message.text
  await update.message.reply_text(
      "Notların alındı! Yapay zeka metinleri düzenleyip Word belgeni"
      " hazırlıyor, lütfen bekle..."
  )

  try:
    rapor_metni = await asyncio.wait_for(
        asyncio.to_thread(raporu_profesyonellestir, context.user_data),
        timeout=90,
    )
  except Exception as hata:
    logging.error(f"Gemini API hatası: {hata}")
    rapor_metni = context.user_data
    await update.message.reply_text(
        f"Yapay zeka adımında sorun oluştu ({type(hata).__name__}), raporun"
        " senin metinlerinle hazırlanıyor..."
    )

  try:
    doc = Document()
    doc.add_heading("HAFTALIK FAALİYET RAPORU", level=0)

    kullanici = update.effective_user.first_name or "Kullanici"
    tarih = datetime.now().strftime("%d.%m.%Y")
    saat = datetime.now().strftime("%H-%M-%S")

    doc.add_paragraph(f"Raporlayan: {kullanici}")
    doc.add_paragraph(f"Tarih: {tarih}")

    doc.add_heading("1. ÇALIŞILAN PROJELER", level=1)
    doc.add_paragraph(rapor_metni["projeler"])

    doc.add_heading("2. TAMAMLANAN GÖREVLER", level=1)
    doc.add_paragraph(rapor_metni["tamamlanan"])

    doc.add_heading("3. DEVAM EDEN İŞLER", level=1)
    doc.add_paragraph(rapor_metni["devam_eden"])

    doc.add_heading("4. LABDA EN ÇOK ZORLANILAN KONU", level=1)
    doc.add_paragraph(rapor_metni["sorunlar"])

    doc.add_heading("5. GELECEK HAFTA PLANI", level=1)
    doc.add_paragraph(rapor_metni["gelecek_plan"])

    doc.add_heading("6. HAFTALIK PUAN", level=1)
    doc.add_paragraph(f"{context.user_data['puan']}/10")

    dosya_adi = f"Haftalik_Rapor_{kullanici}_{tarih}_{saat}.docx"
    doc.save(dosya_adi)

    with open(dosya_adi, "rb") as belge:
      await update.message.reply_document(
          document=belge,
          filename=dosya_adi,
          caption="Haftalık raporun hazır! Word dosyan ektedir.",
      )
    await update.message.reply_text("Rapor Google Drive'a yükleniyor...")
    drive_linki = await asyncio.to_thread(
        upload_docx_to_drive, dosya_adi, dosya_adi
    )
    await update.message.reply_text(
        f"✅ Rapor Google Drive'a başarıyla kaydedildi!\n🔗 Link: {drive_linki}"
    )
  except Exception as dosya_hatasi:
    logging.error(f"Dosya oluşturma hatası: {dosya_hatasi}")
    await update.message.reply_text(
        f"Word dosyası hazırlanırken hata oluştu: {dosya_hatasi}"
    )

  return ConversationHandler.END


async def iptal(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data.clear()
  await update.message.reply_text(
      "Rapor oluşturma iptal edildi. Tekrar başlamak için /yenirapor yazabilirsin."
  )
  return ConversationHandler.END


def main():
  app = Application.builder().token(TELEGRAM_TOKEN).build()

  rapor_konusmasi = ConversationHandler(
      entry_points=[CommandHandler("yenirapor", yeni_rapor)],
      states={
          PROJELER: [
              MessageHandler(filters.TEXT & ~filters.COMMAND, projeler_al)
          ],
          TAMAMLANAN: [
              MessageHandler(filters.TEXT & ~filters.COMMAND, tamamlanan_al)
          ],
          DEVAM_EDEN: [
              MessageHandler(filters.TEXT & ~filters.COMMAND, devam_eden_al)
          ],
          SORUNLAR: [
              MessageHandler(filters.TEXT & ~filters.COMMAND, sorunlar_al)
          ],
          GELECEK_PLAN: [
              MessageHandler(filters.TEXT & ~filters.COMMAND, gelecek_plan_al)
          ],
          PUAN: [
          MessageHandler(filters.TEXT & ~filters.COMMAND, puan_al)
          ],
      },
      fallbacks=[CommandHandler("iptal", iptal)],
  )

  app.add_handler(CommandHandler("start", start))
  app.add_handler(rapor_konusmasi)

  print("Bot çalışıyor! Durdurmak için terminalde Ctrl+C basabilirsin.")
  app.run_polling()


if __name__ == "__main__":
  main()
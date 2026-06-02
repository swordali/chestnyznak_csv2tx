import streamlit as st
import openpyxl
import os

st.set_page_config(page_title="GS1 Data Matrix Bölücü", layout="centered")

st.title("📦 GS1 Data Matrix 5 Sütun Bölücü")
st.write("Excel (.xlsx) dosyanızı yükleyin. Hücrelerinizdeki orijinal karakterler aynen korunarak 5 sütunlu TXT dosyası üretilir.")

uploaded_file = st.file_uploader("Excel Dosyanızı Seçin (.xlsx)", type=["xlsx"])

# Başlık satırlarını akıllıca eleyen süzgeç
def baslik_mi(metin_listesi):
    yasakli = ["purchase", "order", "item", "serial", "code", "group", "product"]
    joined = "".join(metin_listesi).lower()
    return any(kelime in joined for kelime in yasakli)

if uploaded_file is not None:
    orijinal_isim, _ = os.path.splitext(uploaded_file.name)
    try:
        veri_listesi = []
        
        # 1. ADIM: Excel dosyasını tamamen ham haliyle açıyoruz
        wb = openpyxl.load_workbook(uploaded_file, data_only=True)
        sheet = wb.active
        
        for row in sheet.iter_rows(values_only=True):
            # Satırdaki boş olmayan hücreleri yazıya çevirip al
            hucreler = [str(cell).strip() for cell in row if cell is not None]
            
            # Eğer satır boşsa veya başlık kelimeleri içeriyorsa es geç
            if not hucreler or baslik_mi(hucreler):
                continue
            
            # KESİN ÇÖZÜM: Araya hiçbir gizli kod veya ASCII 29 karakteri EKLENMİYOR.
            # Excel hücresinin içinde ne yazıyorsa (ünlem, boşluk, harf) aynen birleştiriliyor.
            tam_satir = "".join(hucreler)
            veri_listesi.append(tam_satir)
            
        toplam_veri = len(veri_listesi)
        st.success(f"⚡ Başarıyla İşlendi! {toplam_veri} adet orijinal veri satırı korundu.")
        
        # 2. ADIM: Veriyi Matematiksel Olarak 5 Sütun Halinde Yan Yana Dizme
        sutun_sayisi = 5
        yeni_satirlar = []
        for i in range(0, toplam_veri, sutun_sayisi):
            grup = veri_listesi[i:i+sutun_sayisi]
            
            # Eğer son satırda 5 sütun dolmazsa eksik yerleri boş bırak
            while len(grup) < sutun_sayisi:
                grup.append("")
                
            # Sütunları yan yana sadece SEKME (\t) karakteri ile birleştir
            yeni_satirlar.append("\t".join(grup))
            
        # Tüm tabloyu alt alta birleştirerek metni tamamla
        final_metin = "\n".join(yeni_satirlar)
        
        # 3. ADIM: UTF-16 formatında bayt çıktısı hazırla
        txt_bayt = final_metin.encode('utf-16')
        
        st.markdown("---")
        # İndirme Butonu
        st.download_button(
            label="📥 5 Sütunlu UTF-16 TXT Dosyasını İndir",
            data=txt_bayt,
            file_name=f"{orijinal_isim}_5sutun_utf16.txt",
            mime="text/plain"
        )
        
    except Exception as e:
        st.error(f"Süreçte bir hata oluştu: {e}")

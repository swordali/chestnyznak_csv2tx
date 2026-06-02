import streamlit as st
import openpyxl
import os

st.set_page_config(page_title="GS1 Data Matrix Bölücü", layout="centered")

st.title("📦 GS1 Data Matrix 5 Sütun Bölücü")
st.write("Excel (.xlsx) dosyanızı yükleyin. ASCII 29 (GS) siyah kutuları tam yerinde korunarak 5 sütunlu TXT üretilir.")

# Güvenlik için sadece Excel dosyalarını kabul ediyoruz
uploaded_file = st.file_uploader("Excel Dosyanızı Seçin (.xlsx)", type=["xlsx"])

# Başlık satırlarını akıllıca listeden eleyen filtre
def baslik_mi(metin):
    yasakli = ["purchase", "order", "item", "serial", "code", "group", "product"]
    return any(kelime in metin.lower() for kelime in yasakli) and len(metin) < 40

if uploaded_file is not None:
    orijinal_isim, _ = os.path.splitext(uploaded_file.name)
    try:
        veri_listesi = []
        
        # 1. ADIM: Excel dosyasını openpyxl ile ham (data_only) açıyoruz
        wb = openpyxl.load_workbook(uploaded_file, data_only=True)
        sheet = wb.active
        
        for row in sheet.iter_rows(values_only=True):
            vals = [str(c).strip() for c in row if c is not None]
            if not vals:
                continue
            
            # Satırdaki verileri birleştir
            satir_metni = "".join(vals)
            
            # Eğer satır başlık metni içeriyorsa işleme dahil etme
            if baslik_mi(satir_metni):
                continue
                
            # 🛡️ KESİN ÇÖZÜM: Excel'in gizlediği kaçış kodunu GERÇEK ASCII 29 (GS) baytına çeviriyoruz.
            # Böylece Notepad++ üzerinde o siyah renkli GS kutusu tam yerinde yeniden canlanır.
            satir_metni = satir_metni.replace("_x001d_", "\x1d").replace("_x001D_", "\x1d")
            veri_listesi.append(satir_metni)
            
        toplam_veri = len(veri_listesi)
        st.success(f"⚡ Başarıyla İşlendi! {toplam_veri} adet orijinal siyah kutulu (GS) kod korumaya alındı.")
        
        # 2. ADIM: Veriyi 5 Sütun Halinde Yan Yana Paketleme (Sıfır Pandas Müdahalesi)
        sutun_sayisi = 5
        yeni_satirlar = []
        for i in range(0, toplam_veri, sutun_sayisi):
            grup = veri_listesi[i:i+sutun_sayisi]
            
            # Eğer son satırda 5 sütun tamamlanmazsa boşluk ekle
            while len(grup) < sutun_sayisi:
                grup.append("")
                
            # Sütunları yan yana sadece SEKME (\t) tuşu ile birleştir. Tırnak işaretlerini asla eklemez.
            yeni_satirlar.append("\t".join(grup))
            
        # Tüm tabloyu alt alta birleştir
        final_metin = "\n".join(yeni_satirlar)
        
        # 3. ADIM: Notepad++ için en doğru kodlama (UTF-16) ile bayta çevir
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

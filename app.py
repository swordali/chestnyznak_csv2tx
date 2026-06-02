import streamlit as st
import openpyxl
import os

st.set_page_config(page_title="GS1 Data Matrix Bölücü", layout="centered")

st.title("📦 GS1 Data Matrix 5 Sütun Bölücü")
st.write("Excel (.xlsx), CSV veya TXT dosyanızı yükleyin. ASCII 29 (GS) siyah kutuları %100 korunarak 5 sütuna bölünür.")

# Her üç formatı da kabul ediyoruz
uploaded_file = st.file_uploader("Dosyanızı Seçin (.xlsx, .csv, .txt)", type=["xlsx", "csv", "txt"])

def baslik_mi(metin):
    yasakli = ["purchase", "order", "item", "serial", "code", "group", "product"]
    return any(kelime in metin.lower() for kelime in yasakli) and len(metin) < 40

if uploaded_file is not None:
    orijinal_isim, uzanti = os.path.splitext(uploaded_file.name)
    try:
        raw_lines = []
        
        # --- 1. ADIM: EXCEL DOSYASINI OKUMA VE GİZLİ _x001d_ ŞİFRELERİNİ ÇÖZME ---
        if uzanti.lower() == '.xlsx':
            wb = openpyxl.load_workbook(uploaded_file, data_only=True)
            sheet = wb.active
            for row in sheet.iter_rows(values_only=True):
                vals = [str(c).strip() for c in row if c is not None]
                if not vals:
                    continue
                
                # Bütün hücreleri birleştir ve Excel'in gizlediği kontrol karakterlerini GERÇEK GS KUTUSUNA çevir
                satir_metni = "".join(vals)
                satir_metni = satir_metni.replace("_x001d_", "\x1d").replace("_x001D_", "\x1d")
                raw_lines.append(satir_metni)
                
        # --- 2. ADIM: CSV VEYA TXT DOSYASINI HAM BAYT OLARAK OKUMA ---
        else:
            bytes_data = uploaded_file.read()
            try:
                metin = bytes_data.decode('utf-8')
            except:
                metin = bytes_data.decode('latin-1')
            raw_lines = metin.splitlines()

        # --- 3. ADIM: BAŞLIKLARI VE GEREKSİZ SATIRLARI TEMİZLEME ---
        veri_listesi = []
        for line in raw_lines:
            line_clean = line.strip()
            if not line_clean or baslik_mi(line_clean):
                continue
            veri_listesi.append(line_clean)
            
        toplam_veri = len(veri_listesi)
        st.success(f"⚡ Başarıyla İşlendi! {toplam_veri} adet siyah kutulu (GS) orijinal kod korumaya alındı.")
        
        # --- 4. ADIM: VERİYİ KUSURSUZCA 5 SÜTUNA BÖLME ---
        sutun_sayisi = 5
        yeni_satirlar = []
        for i in range(0, toplam_veri, sutun_sayisi):
            grup = veri_listesi[i:i+sutun_sayisi]
            
            # Eksik sütunları boş bırak
            while len(grup) < sutun_sayisi:
                grup.append("")
                
            # Sütunları yan yana sadece gerçek SEKME (\t) tuşu ile diz
            yeni_satirlar.append("\t".join(grup))
            
        final_metin = "\n".join(yeni_satirlar)
        
        # --- 5. ADIM: NOTEPAD++ İÇİN EN DOĞRU KODLAMA (UTF-16) ---
        txt_bayt = final_metin.encode('utf-16')
        
        st.markdown("---")
        st.download_button(
            label="📥 5 Sütunlu UTF-16 TXT Dosyasını İndir",
            data=txt_bayt,
            file_name=f"{orijinal_isim}_5sutun_utf16.txt",
            mime="text/plain"
        )
        
    except Exception as e:
        st.error(f"Süreçte bir hata oluştu: {e}")

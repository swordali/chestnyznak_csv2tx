import streamlit as st
import openpyxl
import os

st.set_page_config(page_title="GS1 Data Matrix Splitter", layout="centered")

st.title("📦 GS1 Data Matrix 5 Sütun Bölücü")
st.write("Excel (.xlsx) veya CSV dosyanızı yükleyin. Satırlar hiçbir değişikliğe uğramadan yan yana 5 sütun halinde dizilir.")

# Поддерживаем оба формата, как вы и просили
uploaded_file = st.file_uploader("Dosyanızı Seçin (.xlsx, .csv)", type=["xlsx", "csv"])

def baslik_mi(metin):
    yasakli = ["purchase", "order", "item", "serial", "code", "group", "product"]
    return any(kelime in metin.lower() for kelime in yasakli) and len(metin) < 40

if uploaded_file is not None:
    orijinal_isim, uzanti = os.path.splitext(uploaded_file.name)
    try:
        veri_listesi = []
        
        # --- 1. ЕСЛИ ЗАГРУЖЕН EXCEL (.XLSX) ---
        if uzanti.lower() == '.xlsx':
            wb = openpyxl.load_workbook(uploaded_file, data_only=True)
            sheet = wb.active
            for row in sheet.iter_rows(values_only=True):
                # Собираем все непустые ячейки строки в единый текст БЕЗ разделения
                vals = [str(c).strip() for c in row if c is not None]
                if not vals:
                    continue
                
                satir_metni = "".join(vals)
                if baslik_mi(satir_metni):
                    continue
                
                veri_listesi.append(satir_metni)
                
        # --- 2. ЕСЛИ ЗАГРУЖЕН CSV (Полный обход Pandas) ---
        else:
            bytes_data = uploaded_file.read()
            try:
                metin_icerik = bytes_data.decode('utf-8')
            except:
                metin_icerik = bytes_data.decode('latin-1')
            
            for line in metin_icerik.splitlines():
                line_clean = line.strip()
                if not line_clean or baslik_mi(line_clean):
                    continue
                
                # Убираем только внешние лишние кавычки, если CSV их добавил
                if line_clean.startswith('"') and line_clean.endswith('"'):
                    line_clean = line_clean[1:-1]
                
                veri_listesi.append(line_clean)

        toplam_veri = len(veri_listesi)
        st.success(f"⚡ Başarıyla İşlendi! {toplam_veri} adet orijinal kod listeye alındı.")
        
        # --- 3. РАЗДЕЛЕНИЕ НА 5 СТОЛБЦОВ (Каждые 5 строк склеиваем через TAB) ---
        sutun_sayisi = 5
        yeni_satirlar = []
        for i in range(0, toplam_veri, sutun_sayisi):
            grup = veri_listesi[i:i+sutun_sayisi]
            
            # Если в последней строке меньше 5 элементов, заполняем пустотой
            while len(grup) < sutun_sayisi:
                grup.append("")
                
            # Склеиваем 5 кодов в одну строку через знак табуляции (\t)
            yeni_satirlar.append("\t".join(grup))
            
        final_metin = "\n".join(yeni_satirlar)
        
        # --- 4. КОДИРОВАНИЕ В СТРОГИЙ UTF-16 ДЛЯ NOTEPAD++ ---
        txt_bayt = final_metin.encode('utf-16')
        
        st.markdown("---")
        st.download_button(
            label="📥 5 Sütunlu UTF-16 TXT Dosyasını İndir",
            data=txt_bayt,
            file_name=f"{orijinal_isim}_5sutun_utf16.txt",
            mime="text/plain"
        )
        
    except Exception as e:
        st.error(f"Hata: {e}")

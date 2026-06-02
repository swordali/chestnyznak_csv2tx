import streamlit as st
import numpy as np
import openpyxl
import os

st.set_page_config(page_title="GS1 Data Matrix Bölücü", layout="wide")

st.title("🛡️ GS1 Data Matrix Sütun Bölücü")
st.write("Excel (.xlsx) veya CSV dosyanızı yükleyin. Dağılmış sütunlar ASCII 29 (GS) karakteri eklenerek birleştirilir ve 5 sütuna bölünür.")

uploaded_file = st.file_uploader("Listenizi Seçin (.xlsx, .csv)", type=["xlsx", "csv"])

# Başlık kelimelerini temizleme süzgeci
def baslik_mi(metin):
    yasakli = ["purchase order", "item serial code", "group", "product code", "purchase", "order", "serial", "code"]
    return metin.strip().lower() in yasakli

if uploaded_file is not None:
    orijinal_isim, uzanti = os.path.splitext(uploaded_file.name)
    try:
        ham_gs1_kodlari = []
        
        # --- 1. ADIM: EXCEL (.XLSX) DOSYASINI OKUMA VE GS KARAKTERİ İLE BİRLEŞTİRME ---
        if uzanti.lower() == '.xlsx':
            wb = openpyxl.load_workbook(uploaded_file, data_only=True)
            sheet = wb.active
            
            for row in sheet.iter_rows(values_only=True):
                # Satırdaki boş olmayan hücreleri yazı tipine çevirip alıyoruz
                hucreler = [str(c).strip() for c in row if c is not None]
                if not hucreler:
                    continue
                
                # Eğer ilk hücre başlıksa tüm satırı geç
                if baslik_mi(hucreler[0]):
                    continue
                
                # EKRAN GÖRÜNTÜSÜNDEKİ HATANIN ÇÖZÜMÜ:
                # Eğer veri Excel tarafından sütunlara bölünmüşse, onları araya ASCII 29 (\x1d) koyarak birleştir
                # Eğer zaten tek sütundaysa, olduğu gibi listeye eklenir
                if len(hucreler) >= 3:
                    # Örn: 01046... + GS + 91EE11 + GS + 92XAw...
                    gatin_serial = hucreler[0]
                    crypto_key = hucreler[1]
                    crypto_tail = hucreler[2]
                    tam_kod = f"{gatin_serial}\x1d{crypto_key}\x1d{crypto_tail}"
                else:
                    tam_kod = "".join(hucreler)
                
                ham_gs1_kodlari.append(tam_kod)
                
        # --- 2. ADIM: CSV DOSYASINI OKUMA VE GS KARAKTERİ İLE BİRLEŞTİRME ---
        else:
            dosya_icerik = uploaded_file.read()
            try:
                metin = dosya_icerik.decode('utf-8')
            except:
                metin = dosya_icerik.decode('latin-1')
            
            for line in metin.splitlines():
                line = line.strip()
                if not line:
                    continue
                
                # CSV virgül, noktalı virgül veya sekme (tab) ile ayrılmış olabilir, hepsini kontrol et
                ayirici = None
                for ayir in ['\t', ';', ',']:
                    if ayir in line:
                        ayirici = ayir
                        break
                
                if ayirici:
                    hucreler = [c.strip() for c in line.split(ayirici) if c.strip()]
                    if not hucreler or baslik_mi(hucreler[0]):
                        continue
                    if len(hucreler) >= 3:
                        tam_kod = f"{hucreler[0]}\x1d{hucreler[1]}\x1d{hucreler[2]}"
                    else:
                        tam_kod = "".join(hucreler)
                else:
                    if baslik_mi(line):
                        continue
                    tam_kod = line
                
                ham_gs1_kodlari.append(tam_kod)

        toplam_veri = len(ham_gs1_kodlari)
        st.success(f"Başarıyla İşlendi! {toplam_veri} adet tam ve korunan GS1 satırı elde edildi.")
        
        # --- 3. ADIM: 5 SÜTUNA BÖLME VE SEÇİMLER ---
        col1, col2 = st.columns(2)
        with col1:
            sutun_sayisi = st.number_input("Sütun Sayısı", min_value=1, max_value=20, value=5, step=1)
        with col2:
            kodlama_secim = st.radio("Karakter Kodlaması", ["UTF-16", "UTF-8"])
            
        # 5'li gruplara bölerek matrisi elle oluşturma
        yeni_satirlar = []
        for i in range(0, toplam_veri, sutun_sayisi):
            grup = ham_gs1_kodlari[i:i+sutun_sayisi]
            while len(grup) < sutun_sayisi:
                grup.append("")
            yeni_satirlar.append("\t".join(grup))
            
        final_metin = "\n".join(yeni_satirlar)
        
        # Kodlama ayarlama (UTF-16 LE)
        kodlama = "utf-16" if kodlama_secim == "UTF-16" else "utf-8"
        txt_bayt = final_metin.encode(kodlama)
        
        cikti_dosya_adi = f"{orijinal_isim}_{sutun_sayisi}sutun_{kodlama}.txt"
        
        st.markdown("---")
        st.download_button(
            label="📥 Bölünen TXT Dosyasını İndir",
            data=txt_bayt,
            file_name=cikti_dosya_adi,
            mime="text/plain"
        )
        
    except Exception as e:
        st.error(f"İşlem sırasında bir sorun oluştu: {e}")

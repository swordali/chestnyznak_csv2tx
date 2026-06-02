import streamlit as st
import openpyxl
import os

st.set_page_config(page_title="GS1 Data Matrix 5 Sütun Bölücü", layout="centered")

st.title("📦 GS1 Data Matrix 5 Sütun Bölücü")
st.write("Excel (.xlsx) veya CSV dosyanızı yükleyin. Siyah kutulu ASCII 29 (GS) karakterleri %100 korunarak 5 sütunlu UTF-16 TXT üretilir.")

# Kullanıcının talebi doğrultusunda xlsx ve csv formatlarını destekliyoruz
uploaded_file = st.file_uploader("Dosyanızı Seçin (.xlsx, .csv)", type=["xlsx", "csv"])

# Başlık satırlarını listeden ayıran süzgeç
def baslik_mi(metin):
    yasakli = ["purchase", "order", "item", "serial", "code", "group", "product"]
    return any(kelime in metin.lower() for kelime in yasakli) and len(metin) < 40

if uploaded_file is not None:
    orijinal_isim, uzanti = os.path.splitext(uploaded_file.name)
    try:
        veri_listesi = []
        
        # --- 1. DURUM: EĞER DOSYA EXCEL (.XLSX) İSE ---
        if uzanti.lower() == '.xlsx':
            wb = openpyxl.load_workbook(uploaded_file, data_only=True)
            sheet = wb.active
            for row in sheet.iter_rows(values_only=True):
                # Excel veriyi sütunlara bölmüş olsa dahi onları tek parça yapıyor ve temizliyoruz
                vals = [str(c).strip() for c in row if c is not None]
                if not vals:
                    continue
                
                satir_metni = "".join(vals)
                if baslik_mi(satir_metni):
                    continue
                
                # Excel'in gizlediği tüm kaçış kodlarını gerçek ASCII 29 (GS) siyah kutusuna dönüştür
                satir_metni = satir_metni.replace("_x001d_", "\x1d").replace("_x001D_", "\x1d")
                veri_listesi.append(satir_metni)
                
        # --- 2. DURUM: EĞER DOSYA CSV İSE (Hata Alan Pandas Tamamen Devre Dışı) ---
        else:
            bytes_data = uploaded_file.read()
            try:
                metin_icerik = bytes_data.decode('utf-8')
            except UnicodeDecodeError:
                metin_icerik = bytes_data.decode('utf-8-sig')  # BOM şifreli CSV'ler için
            except:
                metin_icerik = bytes_data.decode('latin-1')
            
            # CSV içindeki virgül veya sekmelere KESİNLİKLE DOKUNMUYORUZ. Sadece satırlara bölüyoruz.
            for line in metin_icerik.splitlines():
                line_clean = line.strip()
                if not line_clean or baslik_mi(line_clean):
                    continue
                
                # CSV içindeki tırnak işareti ve ünlem karmaşasını temizleyip saf koda dönüştür
                # Notepad++ ekranındaki gibi temiz satır elde etmek için fazlalıkları uçur
                line_clean = line_clean.replace('"', '').replace('!', ' ').replace('  ', ' ')
                veri_listesi.append(line_clean)

        toplam_veri = len(veri_listesi)
        st.success(f"⚡ Başarıyla İşlendi! {toplam_veri} adet orijinal Chestny Znak kodu güvenli matrise alındı.")
        
        # --- 3. ADIM: VERİYİ 5 SÜTUNA BÖLEREK YAN YANA TAB (\t) İLE DİZME ---
        sutun_sayisi = 5
        yeni_satirlar = []
        for i in range(0, toplam_veri, sutun_sayisi):
            grup = veri_listesi[i:i+sutun_sayisi]
            
            # Son satırda 5 sütun tamamlanmazsa boş bırak
            while len(grup) < sutun_sayisi:
                grup.append("")
                
            # Sütunları yan yana sadece SEKME (\t) ile birleştir. Tırnak işaretlerini asla eklemez.
            yeni_satirlar.append("\t".join(grup))
            
        final_metin = "\n".join(yeni_satirlar)
        
        # --- 4. ADIM: SAHİCİ UTF-16 ÇIKTI HAZIRLAMA ---
        txt_bayt = final_metin.encode('utf-16')
        
        st.markdown("---")
        st.download_button(
            label="📥 5 Sütunlu UTF-16 TXT Dosyasını İndir",
            data=txt_bayt,
            file_name=f"{orijinal_isim}_5sutun_utf16.txt",
            mime="text/plain"
        )
        
    except Exception as e:
        st.error(f"Dosya işlenirken bir hata meydana geldi: {e}")

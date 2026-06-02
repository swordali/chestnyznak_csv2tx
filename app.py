import streamlit as st
import pandas as pd
import numpy as np
import fitz  # PyMuPDF
from PIL import Image
import zxingcpp
import os
import csv  # Tırnak işaretlerini engellemek için gerekli

st.set_page_config(page_title="GS1 Data Matrix İşlem Merkezi", layout="wide")

st.title("🛡️ GS1 Data Matrix Tarayıcı & Sütun Bölücü")
st.write("Bu uygulama `zxing-cpp` motoru kullanarak görsellerden/PDF'lerden GS1 DataMatrix barkodlarını okuyabilir veya hazır listelerinizi sütunlara bölebilir.")

tab1, tab2 = st.tabs(["📊 Hazır Listeyi Sütunlara Böl", "📷 PDF / Görselden Barkod Oku"])

# ---------------------------------------------------------
# SEKME 1: HAZIR LİSTEYİ BÖLME
# ---------------------------------------------------------
with tab1:
    st.header("Excel veya CSV Listesini Böl")
    uploaded_file = st.file_uploader("Listenizi Seçin (.xlsx, .csv)", type=["xlsx", "csv"], key="file_splitter")

    if uploaded_file is not None:
        orijinal_isim, uzanti = os.path.splitext(uploaded_file.name)
        try:
            # Başlık satırını (Group, Purchase order vb.) atlamak için header=0 yapıyoruz. 
            # Eğer dosyada hiç başlık yoksa ve ilk satırdan veri başlıyorsa header=None yapabilirsiniz.
            if uzanti.lower() == '.xlsx':
                df = pd.read_excel(uploaded_file, header=0)
            else:
                df = pd.read_csv(uploaded_file, header=0)
            
            # İlk sütundaki verileri temiz bir listeye al
            veri_listesi = df.iloc[:, 0].dropna().astype(str).tolist()
            toplam_veri = len(veri_listesi)
            st.success(f"Başarıyla Yüklendi: `{uploaded_file.name}` ({toplam_veri} satır veri bulundu - Başlık satırı atlandı)")
            
            # Ayarlar
            col1, col2, col3 = st.columns(3)
            with col1:
                sutun_sayisi = st.number_input("Sütun Sayanız", min_value=1, max_value=20, value=5, step=1, key="col_num1")
            with col2:
                yon_secim = st.radio("Dizilim Yönü", ["Soldan Sağa (Yatay)", "Yukarıdan Aşağıya (Dikey)"], key="dir1")
            with col3:
                kodlama_secim = st.radio("Karakter Kodlaması (Encoding)", ["UTF-16", "UTF-8"], key="enc1")

            toplam_satir = int(np.ceil(toplam_veri / sutun_sayisi))
            eksik_sayisi = (toplam_satir * sutun_sayisi) - toplam_veri
            if e_sayisi := eksik_sayisi:
                if e_sayisi > 0:
                    veri_listesi.extend([""] * e_sayisi)
                
            if yon_secim == "Soldan Sağa (Yatay)":
                yeni_matris = np.array(veri_listesi).reshape(toplam_satir, sutun_sayisi)
            else:
                yeni_matris = np.array(veri_listesi).reshape(sutun_sayisi, toplam_satir).T
                
            yeni_df = pd.DataFrame(yeni_matris)
            kodlama = "utf-16" if kodlama_secim == "UTF-16" else "utf-8"
            
            # Tırnak işaretlerinin oluşmasını kesin olarak engelleyen parametreler (quoting ve escapechar)
            txt_data = yeni_df.to_csv(sep='\t', index=False, header=False, encoding=kodlama, quoting=csv.QUOTE_NONE, escapechar=" ")
            
            temiz_yon = "yatay" if "Yatay" in yon_secim else "dikey"
            cikti_dosya_adi = f"{orijinal_isim}_{sutun_sayisi}sutun_{temiz_yon}_{kodlama}.txt"
            
            st.download_button(
                label="📥 Bölünen TXT Dosyasını İndir",
                data=txt_data,
                file_name=cikti_dosya_adi,
                mime="text/plain",
                key="btn_dl1"
            )
        except Exception as e:
            st.error(f"Hata: {e}")

# ---------------------------------------------------------
# SEKME 2: ZXING-CPP İLE BARKOD OKUMA (PDF veya GÖRSEL)
# ---------------------------------------------------------
with tab2:
    st.header("zxing-cpp ile Doğrudan Dokümandan Okuma")
    st.info("Buraya yükleyeceğiniz PDF veya resimlerin (PNG/JPG) içindeki DataMatrix kodları taranarak listeye dönüştürülür.")
    
    media_file = st.file_uploader("Barkodlu PDF or Görsel Yükleyin", type=["pdf", "png", "jpg", "jpeg"])
    
    if media_file is not None:
        barkodlar = []
        m_isim, m_uzanti = os.path.splitext(media_file.name)
        
        with st.spinner("zxing-cpp motoru barkodları tarıyor..."):
            try:
                if m_uzanti.lower() == ".pdf":
                    doc = fitz.open(stream=media_file.read(), filetype="pdf")
                    for sayfa_no in range(len(doc)):
                        page = doc.load_page(sayfa_no)
                        pix = page.get_pixmap(dpi=300)
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        
                        results = zxingcpp.read_barcodes(img)
                        for res in results:
                            if res.text:
                                barkodlar.append(res.text)
                else:
                    img = Image.open(media_file)
                    results = zxingcpp.read_barcodes(img)
                    for res in results:
                        if res.text:
                            barkodlar.append(res.text)
                
                if barkodlar:
                    toplam_okunan = len(barkodlar)
                    st.success(f"🎉 Toplam {toplam_okunan} adet DataMatrix barkodu başarıyla okundu!")
                    
                    with st.expander("Okunan Barkod Listesini Gör"):
                        st.write(barkodlar)
                    
                    st.markdown("---")
                    st.subheader("📋 Okunan Barkodları Sütunlara Böl ve İndir")
                    
                    col1_b, col2_b, col3_b = st.columns(3)
                    with col1_b:
                        sutun_b = st.number_input("Sütun Sayısı", min_value=1, max_value=20, value=5, step=1, key="col_num2")
                    with col2_b:
                        yon_b = st.radio("Dizilim Yönü", ["Soldan Sağa (Yatay)", "Yukarıdan Aşağıya (Dikey)"], key="dir2")
                    with col3_b:
                        enc_b = st.radio("Karakter Kodlaması (Encoding)", ["UTF-16", "UTF-8"], key="enc2")
                    
                    t_satir = int(np.ceil(toplam_okunan / sutun_b))
                    e_sayisi = (t_satir * sutun_b) - toplam_okunan
                    if e_sayisi > 0:
                        barkodlar.extend([""] * e_sayisi)
                        
                    if yon_b == "Soldan Sağa (Yatay)":
                        matris_b = np.array(barkodlar).reshape(t_satir, sutun_b)
                    else:
                        matris_b = np.array(barkodlar).reshape(sutun_b, t_satir).T
                        
                    df_b = pd.DataFrame(matris_b)
                    kodlama_b = "utf-16" if enc_b == "UTF-16" else "utf-8"
                    
                    # Tırnak işaretlerinin oluşmasını kesin olarak engelleyen parametreler (quoting ve escapechar)
                    txt_data_b = df_b.to_csv(sep='\t', index=False, header=False, encoding=kodlama_b, quoting=csv.QUOTE_NONE, escapechar=" ")
                    
                    t_yon = "yatay" if "Yatay" in yon_b else "dikey"
                    b_cikti_adi = f"{m_isim}_okunan_{sutun_b}sutun_{t_yon}_{kodlama_b}.txt"
                    
                    st.download_button(
                        label="📥 Okunan Barkodları TXT Olarak İndir",
                        data=txt_data_b,
                        file_name=b_cikti_adi,
                        mime="text/plain",
                        key="btn_dl2"
                    )
                else:
                    st.warning("Belgede veya görselde okunabilir hiçbir DataMatrix barkodu bulunamadı.")
                    
            except Exception as e:
                st.error(f"Barkod tarama esnasında hata oluştu: {e}")

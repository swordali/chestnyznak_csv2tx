import streamlit as st
import os

st.set_page_config(page_title="GS1 Data Matrix Bölücü", layout="centered")

st.title("🛡️ GS1 Data Matrix Sütun Bölücü")
st.write("Ham metin (.txt) dosyanızı yükleyin. Herhangi bir kütüphane veya filtre kullanılmadan ham veri 5 sütuna bölünür.")

# Sadece TXT kabul ediyoruz ki Excel/CSV kütüphaneleri veriyi bozmasın
uploaded_file = st.file_uploader("Listenizi Seçin (.txt)", type=["txt"])

if uploaded_file is not None:
    orijinal_isim, _ = os.path.splitext(uploaded_file.name)
    try:
        # 1. Dosyayı ham bayt olarak oku ve metne çevir (İçindeki gizli karakterleri bozmaz)
        dosya_icerik = uploaded_file.read()
        try:
            metin = dosya_icerik.decode('utf-8')
        except:
            metin = dosya_icerik.decode('latin-1')
        
        # 2. Satırları tertemiz bir listeye al
        ham_satirlar = metin.splitlines()
        
        # Başlıkları eliyoruz
        yasakli_basliklar = ["purchase order", "item serial code", "group", "product code", "purchase  оrder", "item  serial  code"]
        veri_listesi = [s.strip() for s in ham_satirlar if s.strip() and s.strip().lower() not in yasakli_basliklar]
        
        st.success(f"Başarıyla Yüklendi! Toplam {len(veri_listesi)} adet GS1 kodu bulundu.")
        
        # 3. İnteraktif Sorular
        sutun_sayisi = st.number_input("Sütun Sayısı", min_value=1, max_value=20, value=5, step=1)
        kodlama_secim = st.radio("Karakter Kodlaması", ["UTF-16", "UTF-8"])
        
        # 4. Veriyi Matematiksel Bloklar Halinde El ile Yan Yana Dizme (NumPy Yok!)
        yeni_satirlar = []
        for i in range(0, len(veri_listesi), sutun_sayisi):
            # O anki 5'li grubu al (Örn: 0-5 arası, sonra 5-10 arası...)
            grup = veri_listesi[i:i+sutun_sayisi]
            
            # Eğer son grupta 5 eleman yoksa eksik yerleri boşlukla doldur
            while len(grup) < sutun_sayisi:
                grup.append("")
                
            # Elemanları yan yana SEKME (TAB) karakteriyle birleştir
            yeni_satir = "\t".join(grup)
            yeni_satirlar.append(yeni_satir)
            
        # Tüm yeni satırları alt alta birleştirerek tek bir dev metin bloğu yap
        final_metin = "\n".join(yeni_satirlar)
        
        # 5. Seçilen Kodlamaya Göre Dosyayı Bayt Olarak Hazırla
        kodlama = "utf-16" if kodlama_secim == "UTF-16" else "utf-8"
        txt_bayt = final_metin.encode(kodlama)
        
        cikti_dosya_adi = f"{orijinal_isim}_{sutun_sayisi}sutun_{kodlama}.txt"
        
        st.markdown("---")
        # İndirme Butonu
        st.download_button(
            label="📥 Bölünen TXT Dosyasını İndir",
            data=txt_bayt,
            file_name=cikti_dosya_adi,
            mime="text/plain"
        )
        
    except Exception as e:
        st.error(f"Süreçte hata oluştu: {e}")

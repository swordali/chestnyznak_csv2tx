import streamlit as st
import openpyxl
import csv
import io
import os

st.set_page_config(
    page_title="GS1 DataMatrix 5 Sütun Bölücü",
    layout="centered"
)

st.title("📦 GS1 / Chestny ZNAK DataMatrix 5 Sütun Bölücü")

st.write(
    """
Yüklenen XLSX veya CSV dosyasındaki DataMatrix kodları
hiçbir karakter değiştirilmeden okunur ve
5 sütunlu UTF-16 TXT olarak oluşturulur.
"""
)

uploaded_file = st.file_uploader(
    "Dosya Seç (.xlsx veya .csv)",
    type=["xlsx", "csv"]
)

if uploaded_file:

    try:

        veri_listesi = []

        dosya_adi, uzanti = os.path.splitext(uploaded_file.name)

        # ==================================================
        # XLSX
        # ==================================================

        if uzanti.lower() == ".xlsx":

            wb = openpyxl.load_workbook(
                uploaded_file,
                data_only=False,
                read_only=True
            )

            ws = wb.active

            for row in ws.iter_rows(values_only=True):

                if not row:
                    continue

                ilk_dolu = None

                for cell in row:

                    if cell is not None:
                        ilk_dolu = str(cell)
                        break

                if ilk_dolu is None:
                    continue

                veri_listesi.append(ilk_dolu)

        # ==================================================
        # CSV
        # ==================================================

        else:

            raw_bytes = uploaded_file.read()

            encodings = [
                "utf-8-sig",
                "utf-8",
                "utf-16",
                "utf-16-le",
                "utf-16-be",
                "cp1251",
                "latin1"
            ]

            text_data = None

            for enc in encodings:
                try:
                    text_data = raw_bytes.decode(enc)
                    break
                except:
                    pass

            if text_data is None:
                raise Exception("CSV kodlaması okunamadı.")

            reader = csv.reader(io.StringIO(text_data))

            for row in reader:

                if not row:
                    continue

                ilk_hucre = row[0]

                if ilk_hucre == "":
                    continue

                veri_listesi.append(ilk_hucre)

        # ==================================================
        # KONTROL
        # ==================================================

        if len(veri_listesi) == 0:
            st.error("Dosyada okunabilir veri bulunamadı.")
            st.stop()

        st.success(
            f"Toplam {len(veri_listesi)} adet DataMatrix kodu bulundu."
        )

        # ==================================================
        # 5 SÜTUN
        # ==================================================

        sutun_sayisi = 5

        satirlar = []

        for i in range(0, len(veri_listesi), sutun_sayisi):

            grup = veri_listesi[i:i + sutun_sayisi]

            while len(grup) < sutun_sayisi:
                grup.append("")

            satirlar.append("\t".join(grup))

        final_text = "\r\n".join(satirlar)

        # ==================================================
        # UTF16
        # ==================================================

        txt_bytes = final_text.encode("utf-16")

        st.download_button(
            label="📥 UTF-16 TXT İndir",
            data=txt_bytes,
            file_name=f"{dosya_adi}_5sutun_utf16.txt",
            mime="text/plain"
        )

    except Exception as e:
        st.error(f"Hata: {str(e)}")

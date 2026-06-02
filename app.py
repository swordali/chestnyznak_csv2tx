import streamlit as st
import csv
import io

st.set_page_config(
    page_title="Chestny Znak CSV → HP VDP TXT",
    page_icon="📦",
    layout="centered"
)

st.title("Chestny Znak CSV → HP VDP TXT")
st.write(
    "CSV dosyasını yükleyin. İlk sütundaki DataMatrix kodları "
    "5 kolonlu UTF-16 TXT olarak export edilir."
)

uploaded_file = st.file_uploader(
    "CSV Dosyası",
    type=["csv"]
)

if uploaded_file is not None:

    try:
        content = uploaded_file.read()

        encodings = [
            "utf-8",
            "utf-8-sig",
            "cp1251",
            "windows-1251",
            "latin1"
        ]

        csv_text = None

        for enc in encodings:
            try:
                csv_text = content.decode(enc)
                break
            except Exception:
                pass

        if csv_text is None:
            st.error("CSV encoding okunamadı.")
            st.stop()

        reader = csv.reader(io.StringIO(csv_text))

        output_rows = []

        for row in reader:

            if not row:
                continue

            dm = row[0]

            output_rows.append(
                dm + "\t\t\t\t"
            )

        txt_content = "\r\n".join(output_rows)

        txt_bytes = txt_content.encode("utf-16")

        st.success(
            f"{len(output_rows):,} kayıt işlendi."
        )

        st.download_button(
            label="UTF-16 TXT İndir",
            data=txt_bytes,
            file_name="hp_vdp_utf16.txt",
            mime="text/plain"
        )

    except Exception as e:
        st.error(str(e))

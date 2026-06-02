import streamlit as st
import csv
import io

st.set_page_config(
    page_title="Chestny Znak → HP VDP",
    page_icon="📦"
)

st.title("Chestny Znak CSV → HP VDP TXT")

uploaded_file = st.file_uploader(
    "CSV dosyasını yükleyin",
    type=["csv"]
)

if uploaded_file:

    raw_data = uploaded_file.read()

    csv_text = None

    for enc in (
        "utf-8",
        "utf-8-sig",
        "cp1251",
        "windows-1251",
        "latin1"
    ):
        try:
            csv_text = raw_data.decode(enc)
            break
        except Exception:
            pass

    if csv_text is None:
        st.error("CSV encoding okunamadı.")
        st.stop()

    sample = csv_text[:5000]

    try:
        dialect = csv.Sniffer().sniff(
            sample,
            delimiters=";,"
        )
        delimiter = dialect.delimiter
    except Exception:
        delimiter = ";"

    reader = csv.reader(
        io.StringIO(csv_text),
        delimiter=delimiter
    )

    output_lines = []
    total = 0

    for row in reader:

        if not row:
            continue

        dm = row[0]

        if dm is None:
            continue

        dm = str(dm)

        if dm == "":
            continue

        # HP VDP: 5 kolon
        line = dm + "\t\t\t\t"

        output_lines.append(line)
        total += 1

    txt_content = "\r\n".join(output_lines)

    txt_bytes = txt_content.encode("utf-16")

    st.success(f"{total:,} kayıt işlendi")

    st.download_button(
        label="UTF-16 TXT İndir",
        data=txt_bytes,
        file_name="hp_vdp_utf16.txt",
        mime="text/plain"
    )

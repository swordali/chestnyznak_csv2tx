import csv

INPUT_CSV = "source.csv"
OUTPUT_TXT = "output.txt"

with open(INPUT_CSV, "r", encoding="utf-8", newline="") as fin, \
     open(OUTPUT_TXT, "w", encoding="utf-16") as fout:

    reader = csv.reader(fin)

    for row in reader:

        if not row:
            continue

        # İlk sütundaki DataMatrix kodu
        dm = row[0]

        # 5 kolon:
        # Kolon1 = DataMatrix
        # Kolon2-5 = boş
        fout.write(dm + "\t\t\t\t\r\n")

print(f"Oluşturuldu: {OUTPUT_TXT}")

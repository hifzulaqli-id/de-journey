import csv
import re
from datetime import datetime

RAW = "day01/data/orders_raw.csv"
CLEAN = "day01/data/orders_clean.csv"
REJECTED = "day01/data/orders_rejected.csv"
FIELDS = ["order_id", "customer_name", "order_date", "amount", "status"]


def parse_date(text):
    """Ubah beberapa format tanggal menjadi YYYY-MM-DD."""
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(text.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def parse_amount(text):
    """Ambil angka saja: 'Rp150.000' -> 150000."""
    digits = re.sub(r"[^\d]", "", text or "")
    return int(digits) if digits else None


def main():
    clean_rows, rejected_rows = [], []
    seen_ids = set()

    with open(RAW, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name = row["customer_name"].strip().title()
            date = parse_date(row["order_date"])
            amount = parse_amount(row["amount"])
            status = row["status"].strip().lower()
            order_id = row["order_id"].strip()

            # Aturan penolakan
            reason = None
            if order_id in seen_ids:
                reason = "duplikat order_id"
            elif not name:
                reason = "nama kosong"
            elif amount is None:
                reason = "jumlah kosong/tidak valid"
            elif date is None:
                reason = "format tanggal tidak dikenali"

            if reason:
                rejected_rows.append({**row, "reason": reason})
                continue

            seen_ids.add(order_id)
            clean_rows.append({
                "order_id": int(order_id),
                "customer_name": name,
                "order_date": date,
                "amount": amount,
                "status": status,
            })

    with open(CLEAN, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(clean_rows)

    with open(REJECTED, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS + ["reason"])
        writer.writeheader()
        writer.writerows(rejected_rows)

    print(f"Bersih  : {len(clean_rows)} baris")
    print(f"Ditolak : {len(rejected_rows)} baris")


if __name__ == "__main__":
    main()
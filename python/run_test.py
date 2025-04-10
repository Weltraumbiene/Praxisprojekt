import requests
import json
import csv
import time
import threading
import os
import re
from datetime import datetime

# Backend-Konfiguration
BACKEND_URL = "http://localhost:8000/full-check"

# Verzeichnis zum Speichern der Reports
REPORT_DIR = "C:/Users/bfranneck/Desktop/Praxisprojekt/Anwendung/python/reports"
os.makedirs(REPORT_DIR, exist_ok=True)

# Hilfsfunktion für URL -> Dateinamen
def sanitize_url(url: str) -> str:
    clean_url = re.sub(r"https?://", "", url)
    return re.sub(r"\W+", "_", clean_url).strip("_")

# Ladeanzeige mit animierten Punkten
def loading_animation(stop_event):
    dots = ""
    while not stop_event.is_set():
        print(f"\rTest wird ausgeführt. Bitte Geduld{dots}  ", end="", flush=True)
        dots += "."
        if len(dots) > 3:
            dots = ""
        time.sleep(0.5)

# Benutzer-Eingabe
try:
    target_url = input("🌐 Bitte zu scannende URL eingeben (inkl. https://): ").strip()
except KeyboardInterrupt:
    print("\nAbgebrochen.")
    exit(0)

if not target_url.startswith("http"):
    print("❌ Ungültige URL. Bitte mit https:// beginnen.")
    exit(1)

# Ladeanimation starten
stop_event = threading.Event()
loader_thread = threading.Thread(target=loading_animation, args=(stop_event,))
loader_thread.start()

# Anfrage senden
try:
    response = requests.post(BACKEND_URL, json={"url": target_url}, timeout=1000)
    response.raise_for_status()
    try:
        result = response.json()
    except json.JSONDecodeError:
        raise Exception("❌ Fehler: Backend-Antwort ist kein gültiges JSON.")
    pages = result.get("results") or result.get("pages") or []
except Exception as e:
    stop_event.set()
    loader_thread.join()
    print(f"\n❌ Fehler bei der Anfrage: {e}")
    exit(1)

# Ladeanimation beenden
stop_event.set()
loader_thread.join()
print("\n✅ Scan abgeschlossen. Ergebnisse werden gespeichert...\n")

if not pages:
    print("⚠️ Achtung: Keine Ergebnisse erhalten. (Leere Antwort oder keine Unterseiten gefunden)")
else:
    # Dateinamen erstellen mit URL und Zeitstempel
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    base_name = f"scan_{sanitize_url(target_url)}_{timestamp}"
    json_file = os.path.join(REPORT_DIR, f"{base_name}.json")
    csv_file = os.path.join(REPORT_DIR, f"{base_name}.csv")

    # Ergebnisse speichern als JSON
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(pages, f, indent=2, ensure_ascii=False)

    # Ergebnisse speichern als CSV
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["URL", "AXE Errors", "Structural Issues", "CSS Issues", "ARIA Issues", "Warnings", "Total Errors"])
        for entry in pages:
            summary = entry.get("summary", {})
            writer.writerow([
                entry.get("url", "-"),
                summary.get("axe_errors", 0),
                summary.get("structural_issues", 0),
                summary.get("css_issues", 0),
                summary.get("aria_issues", 0),
                summary.get("warnings", 0),
                summary.get("total_errors", 0),
            ])

    print(f"📄 Ergebnisse gespeichert unter:\n- {json_file}\n- {csv_file}")

input("🟢 Bitte Taste drücken um das Programm zu beenden.")

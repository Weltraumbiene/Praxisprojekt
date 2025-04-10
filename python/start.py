import requests
import json
import csv
import time
import threading
import os

# Backend-Konfiguration
BACKEND_URL = "http://localhost:8000/full-check"

# Zielverzeichnis für die Reports
output_dir = r"C:\Users\bfranneck\Desktop\Praxisprojekt\Anwendung\python\reports"
os.makedirs(output_dir, exist_ok=True)

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
    target_url = input("Bitte zu scannende URL eingeben (inkl. https://): ").strip()
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
    response = requests.post(BACKEND_URL, json={"url": target_url})
    response.raise_for_status()
    result = response.json()
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
    # Dateipfade erstellen
    json_file = os.path.join(output_dir, "scan_report.json")
    csv_file = os.path.join(output_dir, "scan_report.csv")

    # JSON speichern
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(pages, f, indent=2, ensure_ascii=False)

    # CSV speichern
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

input("Bitte Taste drücken um das Programm zu beenden.")
